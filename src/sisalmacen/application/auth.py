"""Casos de uso de autenticación y primer arranque."""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sisalmacen.domain.auth import (
    AuthUser,
    ConfigurationRepository,
    DashboardRepository,
    DashboardSnapshot,
    RoleInfo,
    UserRepository,
    UserSummary,
)
from sisalmacen.domain.errors import (
    BusinessRuleViolation,
    ConflictError,
    NotFoundError,
    PermissionDenied,
    ValidationError,
)


@dataclass(frozen=True)
class CurrentSession:
    """Usuario autenticado en la sesión actual."""

    user_id: int
    username: str
    nombre_completo: str
    rol_codigo: str
    rol_nombre: str
    permisos: set[str]
    debe_cambiar_password: bool


@dataclass(frozen=True)
class InitialAdminPayload:
    """Datos requeridos para el primer arranque."""

    empresa_nombre: str
    backup_carpeta: str
    username: str
    nombre_completo: str
    password: str
    confirm_password: str


@dataclass(frozen=True)
class CreateUserPayload:
    """Datos para crear un usuario desde administración."""

    username: str
    nombre_completo: str
    rol_codigo: str
    password: str
    confirm_password: str
    activo: bool = True
    debe_cambiar_password: bool = True


@dataclass(frozen=True)
class UpdateUserPayload:
    """Datos editables de un usuario existente."""

    user_id: int
    username: str
    nombre_completo: str
    rol_codigo: str
    activo: bool


@dataclass(frozen=True)
class ResetUserPasswordPayload:
    """Datos para reinicio administrativo de contraseña."""

    user_id: int
    password: str
    confirm_password: str
    debe_cambiar_password: bool = True


class PasswordHasherPort:
    """Puerto mínimo del servicio de hash de contraseñas."""

    def hash(self, plain_password: str) -> str:
        raise NotImplementedError

    def verify(self, password_hash: str, plain_password: str) -> bool:
        raise NotImplementedError


class InitialSetupService:
    """Gestiona el primer arranque del sistema local."""

    _PASSWORD_POLICY_KEY = "seguridad.password_min_longitud"  # noqa: S105

    def __init__(
        self,
        user_repository: UserRepository,
        configuration_repository: ConfigurationRepository,
        password_hasher: PasswordHasherPort,
    ) -> None:
        self._user_repository = user_repository
        self._configuration_repository = configuration_repository
        self._password_hasher = password_hasher

    def requires_initial_setup(self) -> bool:
        """Indica si aún no existe ningún usuario."""

        return self._user_repository.count_users() == 0

    def create_initial_admin(self, payload: InitialAdminPayload) -> AuthUser:
        """Crea el primer usuario ADMIN y la configuración básica."""

        if not self.requires_initial_setup():
            raise ConflictError(
                "El asistente inicial solo puede ejecutarse cuando no existen usuarios.",
                code="SETUP_YA_REALIZADO",
            )

        empresa_nombre = payload.empresa_nombre.strip()
        username = payload.username.strip()
        nombre_completo = payload.nombre_completo.strip()
        backup_carpeta = payload.backup_carpeta.strip()
        password = payload.password
        confirm_password = payload.confirm_password

        if not empresa_nombre:
            raise ValidationError(
                "Debe indicar el nombre de la empresa.",
                code="EMPRESA_NOMBRE_REQUERIDO",
            )
        if not username:
            raise ValidationError(
                "Debe indicar el usuario administrador.",
                code="USUARIO_REQUERIDO",
            )
        if not nombre_completo:
            raise ValidationError(
                "Debe indicar el nombre completo del administrador.",
                code="NOMBRE_REQUERIDO",
            )
        if password != confirm_password:
            raise ValidationError(
                "La confirmación de contraseña no coincide.",
                code="PASSWORD_NO_COINCIDE",
            )

        password_min_length = self._get_password_min_length()
        if len(password) < password_min_length:
            raise ValidationError(
                f"La contraseña debe tener al menos {password_min_length} caracteres.",
                code="PASSWORD_POLITICA",
            )

        admin_role = self._user_repository.get_role_by_code("ADMIN")
        if admin_role is None:
            raise NotFoundError(
                "No se encontró el rol ADMIN en la configuración inicial.",
                code="ROL_ADMIN_NO_ENCONTRADO",
            )

        admin_user = AuthUser(
            id=None,
            username=username,
            nombre_completo=nombre_completo,
            password_hash=self._password_hasher.hash(password),
            rol_id=admin_role.id,
            rol_codigo=admin_role.codigo,
            rol_nombre=admin_role.nombre,
            activo=True,
            debe_cambiar_password=False,
            intentos_fallidos=0,
            bloqueado_hasta=None,
            ultimo_login=None,
        )
        created_user = self._user_repository.add(admin_user)
        self._configuration_repository.set_many(
            {
                "empresa.nombre": empresa_nombre,
                "backup.carpeta": backup_carpeta,
            }
        )
        return created_user

    def _get_password_min_length(self) -> int:
        values = self._configuration_repository.get_many([self._PASSWORD_POLICY_KEY])
        raw_length = values.get(self._PASSWORD_POLICY_KEY, "8")
        return int(raw_length)


class AuthenticationService:
    """Valida credenciales y construye la sesión del usuario."""

    _CONFIG_KEYS = ("seguridad.max_intentos", "seguridad.bloqueo_minutos")

    def __init__(
        self,
        user_repository: UserRepository,
        configuration_repository: ConfigurationRepository,
        password_hasher: PasswordHasherPort,
    ) -> None:
        self._user_repository = user_repository
        self._configuration_repository = configuration_repository
        self._password_hasher = password_hasher

    def authenticate(self, username: str, password: str) -> CurrentSession:
        """Autentica un usuario y actualiza el estado de acceso."""

        normalized_username = username.strip()
        if not normalized_username or not password:
            raise ValidationError(
                "Debe ingresar usuario y contraseña.",
                code="AUTH_REQUERIDA",
            )

        user = self._user_repository.get_by_username(normalized_username)
        if user is None:
            raise ValidationError(
                "Usuario o contraseña incorrectos.",
                code="AUTH_INVALIDA",
            )

        if not user.activo:
            raise ValidationError(
                "El usuario está desactivado.",
                code="AUTH_INACTIVO",
            )

        config_values = self._configuration_repository.get_many(self._CONFIG_KEYS)
        max_attempts = int(config_values.get("seguridad.max_intentos", "5"))
        bloqueo_minutos = int(config_values.get("seguridad.bloqueo_minutos", "15"))

        now = _utc_now()
        blocked_until = _parse_utc(user.bloqueado_hasta)
        if blocked_until is not None and blocked_until > now:
            restantes = max(1, int((blocked_until - now).total_seconds() // 60) + 1)
            raise ValidationError(
                f"Cuenta bloqueada temporalmente. Intente en {restantes} minutos.",
                code="AUTH_BLOQUEADO",
            )

        if not self._password_hasher.verify(user.password_hash, password):
            failed_attempts = user.intentos_fallidos + 1
            user.intentos_fallidos = failed_attempts
            user.bloqueado_hasta = None
            if failed_attempts >= max_attempts:
                user.bloqueado_hasta = _format_utc(now + timedelta(minutes=bloqueo_minutos))
                user.intentos_fallidos = 0
            self._user_repository.save(user)
            raise ValidationError(
                "Usuario o contraseña incorrectos.",
                code="AUTH_INVALIDA",
            )

        user.intentos_fallidos = 0
        user.bloqueado_hasta = None
        user.ultimo_login = _format_utc(now)
        self._user_repository.save(user)
        return CurrentSession(
            user_id=_require_user_id(user),
            username=user.username,
            nombre_completo=user.nombre_completo,
            rol_codigo=user.rol_codigo,
            rol_nombre=user.rol_nombre,
            permisos=self._user_repository.list_permission_codes(user.rol_id),
            debe_cambiar_password=user.debe_cambiar_password,
        )


class LocalSessionService:
    """Sesión implícita del modo local: sin login ni registro de empresa.

    La auditoría y los movimientos exigen un usuario; este servicio garantiza uno
    ADMIN y deja la configuración mínima lista sin pedir datos al operador.
    """

    LOCAL_USERNAME = "local"
    LOCAL_FULL_NAME = "Operador local"

    def __init__(
        self,
        user_repository: UserRepository,
        configuration_repository: ConfigurationRepository,
        password_hasher: PasswordHasherPort,
    ) -> None:
        self._user_repository = user_repository
        self._configuration_repository = configuration_repository
        self._password_hasher = password_hasher

    def start(self, *, company_name: str, backup_folder: str) -> CurrentSession:
        """Completa la configuración faltante y devuelve la sesión local."""

        self._ensure_defaults(company_name=company_name, backup_folder=backup_folder)
        user = self._resolve_local_user()
        return CurrentSession(
            user_id=_require_user_id(user),
            username=user.username,
            nombre_completo=user.nombre_completo,
            rol_codigo=user.rol_codigo,
            rol_nombre=user.rol_nombre,
            permisos=self._user_repository.list_permission_codes(user.rol_id),
            debe_cambiar_password=False,
        )

    def _ensure_defaults(self, *, company_name: str, backup_folder: str) -> None:
        current = self._configuration_repository.get_many(["empresa.nombre", "backup.carpeta"])
        missing: dict[str, str] = {}
        if not current.get("empresa.nombre", "").strip():
            missing["empresa.nombre"] = company_name
        if not current.get("backup.carpeta", "").strip():
            missing["backup.carpeta"] = backup_folder
        if missing:
            self._configuration_repository.set_many(missing)

    def _resolve_local_user(self) -> AuthUser:
        for summary in self._user_repository.list_users():
            if summary.activo and summary.rol_codigo == "ADMIN":
                user = self._user_repository.get_by_id(summary.id)
                if user is not None:
                    return user

        admin_role = self._user_repository.get_role_by_code("ADMIN")
        if admin_role is None:
            raise NotFoundError(
                "No se encontró el rol ADMIN en la configuración inicial.",
                code="ROL_ADMIN_NO_ENCONTRADO",
            )

        existing = self._user_repository.get_by_username(self.LOCAL_USERNAME)
        if existing is not None:
            existing.activo = True
            existing.rol_id = admin_role.id
            existing.rol_codigo = admin_role.codigo
            existing.rol_nombre = admin_role.nombre
            self._user_repository.save(existing)
            return existing

        # Hash de un secreto aleatorio descartado: el usuario local no tiene contraseña usable.
        unusable_secret = secrets.token_urlsafe(32)
        return self._user_repository.add(
            AuthUser(
                id=None,
                username=self.LOCAL_USERNAME,
                nombre_completo=self.LOCAL_FULL_NAME,
                password_hash=self._password_hasher.hash(unusable_secret),
                rol_id=admin_role.id,
                rol_codigo=admin_role.codigo,
                rol_nombre=admin_role.nombre,
                activo=True,
                debe_cambiar_password=False,
                intentos_fallidos=0,
                bloqueado_hasta=None,
                ultimo_login=None,
            )
        )


class ChangePasswordService:
    """Gestiona el cambio de contraseña del usuario autenticado."""

    _PASSWORD_POLICY_KEY = "seguridad.password_min_longitud"  # noqa: S105

    def __init__(
        self,
        user_repository: UserRepository,
        configuration_repository: ConfigurationRepository,
        password_hasher: PasswordHasherPort,
    ) -> None:
        self._user_repository = user_repository
        self._configuration_repository = configuration_repository
        self._password_hasher = password_hasher

    def change_password(
        self,
        *,
        user_id: int,
        current_password: str,
        new_password: str,
        confirm_password: str,
    ) -> None:
        """Actualiza la contraseña del usuario y limpia el cambio obligatorio."""

        user = self._user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(
                "No se encontró el usuario solicitado.",
                code="USUARIO_NO_ENCONTRADO",
            )

        if not current_password:
            raise ValidationError(
                "Debe ingresar la contraseña actual.",
                code="PASSWORD_ACTUAL_REQUERIDA",
            )
        if not new_password:
            raise ValidationError(
                "Debe ingresar la nueva contraseña.",
                code="PASSWORD_NUEVA_REQUERIDA",
            )
        if new_password != confirm_password:
            raise ValidationError(
                "La confirmación de contraseña no coincide.",
                code="PASSWORD_NO_COINCIDE",
            )
        if not self._password_hasher.verify(user.password_hash, current_password):
            raise ValidationError(
                "La contraseña actual es incorrecta.",
                code="PASSWORD_ACTUAL_INVALIDA",
            )

        password_min_length = self._get_password_min_length()
        if len(new_password) < password_min_length:
            raise ValidationError(
                f"La contraseña debe tener al menos {password_min_length} caracteres.",
                code="PASSWORD_POLITICA",
            )

        user.password_hash = self._password_hasher.hash(new_password)
        user.debe_cambiar_password = False
        self._user_repository.save(user)

    def _get_password_min_length(self) -> int:
        values = self._configuration_repository.get_many([self._PASSWORD_POLICY_KEY])
        raw_length = values.get(self._PASSWORD_POLICY_KEY, "8")
        return int(raw_length)


class AuthorizationService:
    """Valida permisos funcionales de la sesión actual."""

    def require_permission(self, session: CurrentSession, permission_code: str) -> None:
        """Exige un permiso específico y falla con código funcional estable."""

        if permission_code not in session.permisos:
            raise PermissionDenied(
                "No tiene permiso para realizar esta acción.",
                code="SIN_PERMISO",
            )


class UserManagementService:
    """Gestiona usuarios y asignación de roles."""

    _PASSWORD_POLICY_KEY = "seguridad.password_min_longitud"  # noqa: S105
    _MANAGE_PERMISSION = "usuarios.gestionar"

    def __init__(
        self,
        user_repository: UserRepository,
        configuration_repository: ConfigurationRepository,
        password_hasher: PasswordHasherPort,
        authorization_service: AuthorizationService | None = None,
    ) -> None:
        self._user_repository = user_repository
        self._configuration_repository = configuration_repository
        self._password_hasher = password_hasher
        self._authorization_service = authorization_service or AuthorizationService()

    def list_roles(self, current_session: CurrentSession) -> list[RoleInfo]:
        """Lista roles disponibles para la UI administrativa."""

        self._authorization_service.require_permission(current_session, self._MANAGE_PERMISSION)
        return self._user_repository.list_roles()

    def list_users(self, current_session: CurrentSession) -> list[UserSummary]:
        """Devuelve usuarios registrados ordenados por nombre de acceso."""

        self._authorization_service.require_permission(current_session, self._MANAGE_PERMISSION)
        return self._user_repository.list_users()

    def create_user(self, current_session: CurrentSession, payload: CreateUserPayload) -> AuthUser:
        """Crea un usuario con contraseña temporal o definitiva."""

        self._authorization_service.require_permission(current_session, self._MANAGE_PERMISSION)
        username = payload.username.strip()
        nombre_completo = payload.nombre_completo.strip()
        if not username:
            raise ValidationError(
                "Debe indicar el usuario.",
                code="USUARIO_REQUERIDO",
            )
        if not nombre_completo:
            raise ValidationError(
                "Debe indicar el nombre completo.",
                code="NOMBRE_REQUERIDO",
            )
        if payload.password != payload.confirm_password:
            raise ValidationError(
                "La confirmación de contraseña no coincide.",
                code="PASSWORD_NO_COINCIDE",
            )

        self._validate_password_policy(payload.password)
        self._ensure_username_available(username)
        role = self._require_role(payload.rol_codigo)
        user = AuthUser(
            id=None,
            username=username,
            nombre_completo=nombre_completo,
            password_hash=self._password_hasher.hash(payload.password),
            rol_id=role.id,
            rol_codigo=role.codigo,
            rol_nombre=role.nombre,
            activo=payload.activo,
            debe_cambiar_password=payload.debe_cambiar_password,
            intentos_fallidos=0,
            bloqueado_hasta=None,
            ultimo_login=None,
        )
        return self._user_repository.add(user)

    def update_user(self, current_session: CurrentSession, payload: UpdateUserPayload) -> None:
        """Actualiza datos básicos, rol y estado lógico de un usuario."""

        self._authorization_service.require_permission(current_session, self._MANAGE_PERMISSION)
        user = self._require_user(payload.user_id)
        username = payload.username.strip()
        nombre_completo = payload.nombre_completo.strip()
        if not username:
            raise ValidationError(
                "Debe indicar el usuario.",
                code="USUARIO_REQUERIDO",
            )
        if not nombre_completo:
            raise ValidationError(
                "Debe indicar el nombre completo.",
                code="NOMBRE_REQUERIDO",
            )

        self._ensure_username_available(username, exclude_user_id=payload.user_id)
        role = self._require_role(payload.rol_codigo)
        self._validate_user_state_transition(
            current_session=current_session,
            user=user,
            target_role_code=role.codigo,
            target_active=payload.activo,
        )

        user.username = username
        user.nombre_completo = nombre_completo
        user.rol_id = role.id
        user.rol_codigo = role.codigo
        user.rol_nombre = role.nombre
        user.activo = payload.activo
        self._user_repository.save(user)

    def reset_password(self, current_session: CurrentSession, payload: ResetUserPasswordPayload) -> None:
        """Reinicia la contraseña de un usuario y fuerza cambio al ingresar."""

        self._authorization_service.require_permission(current_session, self._MANAGE_PERMISSION)
        user = self._require_user(payload.user_id)
        if payload.password != payload.confirm_password:
            raise ValidationError(
                "La confirmación de contraseña no coincide.",
                code="PASSWORD_NO_COINCIDE",
            )

        self._validate_password_policy(payload.password)
        user.password_hash = self._password_hasher.hash(payload.password)
        user.debe_cambiar_password = payload.debe_cambiar_password
        user.intentos_fallidos = 0
        user.bloqueado_hasta = None
        self._user_repository.save(user)

    def _require_user(self, user_id: int) -> AuthUser:
        user = self._user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(
                "No se encontró el usuario solicitado.",
                code="USUARIO_NO_ENCONTRADO",
            )
        return user

    def _require_role(self, role_code: str) -> RoleInfo:
        role = self._user_repository.get_role_by_code(role_code.strip())
        if role is None:
            raise NotFoundError(
                "No se encontró el rol solicitado.",
                code="ROL_NO_ENCONTRADO",
            )
        return role

    def _ensure_username_available(
        self,
        username: str,
        *,
        exclude_user_id: int | None = None,
    ) -> None:
        existing = self._user_repository.get_by_username(username)
        if existing is None:
            return
        if exclude_user_id is not None and existing.id == exclude_user_id:
            return
        raise ConflictError(
            f"Ya existe un usuario con el nombre '{username}'.",
            code="USUARIO_DUPLICADO",
        )

    def _validate_password_policy(self, password: str) -> None:
        if not password:
            raise ValidationError(
                "Debe ingresar una contraseña.",
                code="PASSWORD_REQUERIDA",
            )
        password_min_length = self._get_password_min_length()
        if len(password) < password_min_length:
            raise ValidationError(
                f"La contraseña debe tener al menos {password_min_length} caracteres.",
                code="PASSWORD_POLITICA",
            )

    def _validate_user_state_transition(
        self,
        *,
        current_session: CurrentSession,
        user: AuthUser,
        target_role_code: str,
        target_active: bool,
    ) -> None:
        if user.id == current_session.user_id and not target_active:
            raise BusinessRuleViolation(
                "No puede desactivar su propio usuario.",
                code="USUARIO_PROPIO",
            )

        admin_loses_admin_privileges = user.activo and user.rol_codigo == "ADMIN" and (
            not target_active or target_role_code != "ADMIN"
        )
        if admin_loses_admin_privileges and self._user_repository.count_active_admins() <= 1:
            raise BusinessRuleViolation(
                "No puede desactivar al último administrador activo.",
                code="ULTIMO_ADMIN",
            )

    def _get_password_min_length(self) -> int:
        values = self._configuration_repository.get_many([self._PASSWORD_POLICY_KEY])
        raw_length = values.get(self._PASSWORD_POLICY_KEY, "8")
        return int(raw_length)


class DashboardService:
    """Obtiene el resumen mostrado al entrar a la aplicación."""

    def __init__(self, dashboard_repository: DashboardRepository) -> None:
        self._dashboard_repository = dashboard_repository

    def get_snapshot(self) -> DashboardSnapshot:
        """Devuelve el estado agregado del sistema local."""

        return self._dashboard_repository.get_snapshot()


def _utc_now() -> datetime:
    return datetime.now(tz=UTC)


def _format_utc(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_utc(value: str | None) -> datetime | None:
    if value is None or not value:
        return None
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)


def _require_user_id(user: AuthUser) -> int:
    if user.id is None:
        raise RuntimeError("El usuario autenticado no tiene identificador persistido.")
    return user.id
