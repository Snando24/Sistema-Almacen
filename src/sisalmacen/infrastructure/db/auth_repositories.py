"""Repositorios de autenticación y resumen inicial."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from sisalmacen.domain.auth import (
    AuthUser,
    ConfigurationRepository,
    DashboardRepository,
    DashboardSnapshot,
    RoleInfo,
    UserSummary,
    UserRepository,
)
from sisalmacen.infrastructure.db.import_settings_repositories import build_dashboard_snapshot
from sisalmacen.infrastructure.db.models import (
    Configuracion,
    Permiso,
    Rol,
    RolPermiso,
    Usuario,
)


class SqlAlchemyUserRepository(UserRepository):
    """Implementación SQLAlchemy para autenticación."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def count_users(self) -> int:
        return self._scalar(select(func.count(Usuario.id)))

    def count_active_users(self) -> int:
        return self._scalar(select(func.count(Usuario.id)).where(Usuario.activo == 1))

    def get_by_id(self, user_id: int) -> AuthUser | None:
        statement = (
            select(Usuario, Rol)
            .join(Rol, Rol.id == Usuario.rol_id)
            .where(Usuario.id == user_id)
        )
        row = self._session.execute(statement).one_or_none()
        if row is None:
            return None
        user_model, role_model = row
        return _map_auth_user(user_model, role_model)

    def get_by_username(self, username: str) -> AuthUser | None:
        statement = (
            select(Usuario, Rol)
            .join(Rol, Rol.id == Usuario.rol_id)
            .where(Usuario.username == username.strip())
        )
        row = self._session.execute(statement).one_or_none()
        if row is None:
            return None
        user_model, role_model = row
        return _map_auth_user(user_model, role_model)

    def add(self, user: AuthUser) -> AuthUser:
        user_model = Usuario(
            username=user.username,
            nombre_completo=user.nombre_completo,
            password_hash=user.password_hash,
            rol_id=user.rol_id,
            activo=1 if user.activo else 0,
            debe_cambiar_password=1 if user.debe_cambiar_password else 0,
            intentos_fallidos=user.intentos_fallidos,
            bloqueado_hasta=user.bloqueado_hasta,
            ultimo_login=user.ultimo_login,
        )
        self._session.add(user_model)
        self._session.flush()
        role = self.get_role_by_code(user.rol_codigo)
        if role is None:
            raise RuntimeError("No se pudo rehidratar el rol del usuario creado.")
        return AuthUser(
            id=user_model.id,
            username=user_model.username,
            nombre_completo=user_model.nombre_completo,
            password_hash=user_model.password_hash,
            rol_id=user_model.rol_id,
            rol_codigo=role.codigo,
            rol_nombre=role.nombre,
            activo=bool(user_model.activo),
            debe_cambiar_password=bool(user_model.debe_cambiar_password),
            intentos_fallidos=user_model.intentos_fallidos,
            bloqueado_hasta=user_model.bloqueado_hasta,
            ultimo_login=user_model.ultimo_login,
        )

    def save(self, user: AuthUser) -> None:
        if user.id is None:
            raise RuntimeError("No se puede guardar un usuario sin id.")
        model = self._session.get(Usuario, user.id)
        if model is None:
            raise RuntimeError("No se encontró el usuario a actualizar.")
        model.nombre_completo = user.nombre_completo
        model.password_hash = user.password_hash
        model.rol_id = user.rol_id
        model.activo = 1 if user.activo else 0
        model.debe_cambiar_password = 1 if user.debe_cambiar_password else 0
        model.intentos_fallidos = user.intentos_fallidos
        model.bloqueado_hasta = user.bloqueado_hasta
        model.ultimo_login = user.ultimo_login

    def get_role_by_code(self, code: str) -> RoleInfo | None:
        model = self._session.execute(
            select(Rol).where(Rol.codigo == code.strip())
        ).scalar_one_or_none()
        if model is None:
            return None
        return RoleInfo(id=model.id, codigo=model.codigo, nombre=model.nombre)

    def list_roles(self) -> list[RoleInfo]:
        statement = select(Rol).order_by(Rol.nombre, Rol.codigo)
        return [
            RoleInfo(id=model.id, codigo=model.codigo, nombre=model.nombre)
            for model in self._session.execute(statement).scalars().all()
        ]

    def list_users(self) -> list[UserSummary]:
        statement = select(Usuario, Rol).join(Rol, Rol.id == Usuario.rol_id).order_by(Usuario.username)
        rows = self._session.execute(statement).all()
        return [_map_user_summary(user_model, role_model) for user_model, role_model in rows]

    def count_active_admins(self) -> int:
        statement = (
            select(func.count(Usuario.id))
            .join(Rol, Rol.id == Usuario.rol_id)
            .where(Usuario.activo == 1, Rol.codigo == "ADMIN")
        )
        return self._scalar(statement)

    def list_permission_codes(self, role_id: int) -> set[str]:
        statement = (
            select(Permiso.codigo)
            .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
            .where(RolPermiso.rol_id == role_id)
            .order_by(Permiso.codigo)
        )
        return set(self._session.execute(statement).scalars().all())

    def _scalar(self, statement: Select[tuple[int]]) -> int:
        return int(self._session.execute(statement).scalar_one())


class SqlAlchemyConfigurationRepository(ConfigurationRepository):
    """Configuración persistida sobre SQLite."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_many(self, keys: Sequence[str]) -> dict[str, str]:
        if not keys:
            return {}
        statement = select(Configuracion).where(Configuracion.clave.in_(list(keys)))
        rows = self._session.execute(statement).scalars().all()
        return {row.clave: row.valor for row in rows}

    def set_many(self, values: Mapping[str, str]) -> None:
        for key, value in values.items():
            row = self._session.get(Configuracion, key)
            if row is None:
                row = Configuracion(clave=key, valor=value, descripcion=None)
                self._session.add(row)
                continue
            row.valor = value


class SqlAlchemyDashboardRepository(DashboardRepository):
    """Resumen inicial mostrado en la aplicación."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_snapshot(self) -> DashboardSnapshot:
        return build_dashboard_snapshot(self._session)


def _map_auth_user(user_model: Usuario, role_model: Rol) -> AuthUser:
    return AuthUser(
        id=user_model.id,
        username=user_model.username,
        nombre_completo=user_model.nombre_completo,
        password_hash=user_model.password_hash,
        rol_id=user_model.rol_id,
        rol_codigo=role_model.codigo,
        rol_nombre=role_model.nombre,
        activo=bool(user_model.activo),
        debe_cambiar_password=bool(user_model.debe_cambiar_password),
        intentos_fallidos=user_model.intentos_fallidos,
        bloqueado_hasta=user_model.bloqueado_hasta,
        ultimo_login=user_model.ultimo_login,
    )


def _map_user_summary(user_model: Usuario, role_model: Rol) -> UserSummary:
    return UserSummary(
        id=user_model.id,
        username=user_model.username,
        nombre_completo=user_model.nombre_completo,
        rol_id=user_model.rol_id,
        rol_codigo=role_model.codigo,
        rol_nombre=role_model.nombre,
        activo=bool(user_model.activo),
        debe_cambiar_password=bool(user_model.debe_cambiar_password),
        bloqueado_hasta=user_model.bloqueado_hasta,
        ultimo_login=user_model.ultimo_login,
    )
