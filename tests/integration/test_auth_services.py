"""Pruebas de primer arranque y autenticación."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from sisalmacen.application.auth import (
    AuthenticationService,
    AuthorizationService,
    ChangePasswordService,
    CreateUserPayload,
    CurrentSession,
    InitialAdminPayload,
    InitialSetupService,
    LocalSessionService,
    ResetUserPasswordPayload,
    UpdateUserPayload,
    UserManagementService,
)
from sisalmacen.domain.errors import BusinessRuleViolation, PermissionDenied, ValidationError
from sisalmacen.infrastructure.db.auth_repositories import (
    SqlAlchemyConfigurationRepository,
    SqlAlchemyUserRepository,
)
from sisalmacen.infrastructure.db.bootstrap import run_migrations
from sisalmacen.infrastructure.db.models import Configuracion, Usuario
from sisalmacen.infrastructure.db.session import create_session_factory, create_sqlite_engine
from sisalmacen.infrastructure.security.passwords import Argon2PasswordHasher

TEST_PASSWORD = "Secreta123"  # noqa: S105


def _start_local_session(session_factory: sessionmaker[Session]) -> CurrentSession:
    with session_factory() as session:
        service = LocalSessionService(
            user_repository=SqlAlchemyUserRepository(session),
            configuration_repository=SqlAlchemyConfigurationRepository(session),
            password_hasher=Argon2PasswordHasher(),
        )
        current_session = service.start(company_name="R&R Grupo", backup_folder="C:/Respaldos")
        session.commit()
    return current_session


def test_local_session_creates_admin_and_defaults_without_user_input(
    tmp_path: Path,
    project_root: Path,
) -> None:
    session_factory = _build_session_factory(tmp_path, project_root)

    current_session = _start_local_session(session_factory)

    assert current_session.username == "local"
    assert current_session.rol_codigo == "ADMIN"
    assert "movimientos.entrada" in current_session.permisos
    with session_factory() as session:
        assert session.get(Configuracion, "empresa.nombre").valor == "R&R Grupo"  # type: ignore[union-attr]
        assert session.get(Configuracion, "backup.carpeta").valor == "C:/Respaldos"  # type: ignore[union-attr]


def test_local_session_is_idempotent_and_keeps_existing_config(
    tmp_path: Path,
    project_root: Path,
) -> None:
    session_factory = _build_session_factory(tmp_path, project_root)
    first = _start_local_session(session_factory)
    with session_factory() as session:
        session.get(Configuracion, "empresa.nombre").valor = "Otra empresa"  # type: ignore[union-attr]
        session.commit()

    second = _start_local_session(session_factory)

    assert second.user_id == first.user_id
    with session_factory() as session:
        assert session.get(Configuracion, "empresa.nombre").valor == "Otra empresa"  # type: ignore[union-attr]
        assert SqlAlchemyUserRepository(session).count_users() == 1


def test_local_session_reuses_existing_active_admin(
    tmp_path: Path,
    project_root: Path,
) -> None:
    session_factory = _build_session_factory(tmp_path, project_root)
    _seed_admin(session_factory)

    current_session = _start_local_session(session_factory)

    assert current_session.username == "admin"
    with session_factory() as session:
        assert SqlAlchemyUserRepository(session).count_users() == 1

def test_initial_setup_creates_admin_and_company_config(
    tmp_path: Path,
    project_root: Path,
) -> None:
    session_factory = _build_session_factory(tmp_path, project_root)

    with session_factory() as session:
        service = InitialSetupService(
            user_repository=SqlAlchemyUserRepository(session),
            configuration_repository=SqlAlchemyConfigurationRepository(session),
            password_hasher=Argon2PasswordHasher(),
        )
        created_user = service.create_initial_admin(
            InitialAdminPayload(
                empresa_nombre="Almacén Central",
                backup_carpeta="C:/Respaldos",
                username="admin",
                nombre_completo="Administrador General",
                password=TEST_PASSWORD,  # noqa: S106
                confirm_password=TEST_PASSWORD,  # noqa: S106
            )
        )
        session.commit()

    assert created_user.id is not None
    assert created_user.rol_codigo == "ADMIN"

    with session_factory() as session:
        user_repo = SqlAlchemyUserRepository(session)
        config_empresa = session.get(Configuracion, "empresa.nombre")
        config_backup = session.get(Configuracion, "backup.carpeta")

        stored_user = user_repo.get_by_username("admin")

    assert stored_user is not None
    assert stored_user.nombre_completo == "Administrador General"
    assert stored_user.password_hash != TEST_PASSWORD  # noqa: S105
    assert config_empresa is not None
    assert config_empresa.valor == "Almacén Central"
    assert config_backup is not None
    assert config_backup.valor == "C:/Respaldos"


def test_authentication_accepts_valid_credentials(
    tmp_path: Path,
    project_root: Path,
) -> None:
    session_factory = _build_session_factory(tmp_path, project_root)
    _seed_admin(session_factory)

    with session_factory() as session:
        service = AuthenticationService(
            user_repository=SqlAlchemyUserRepository(session),
            configuration_repository=SqlAlchemyConfigurationRepository(session),
            password_hasher=Argon2PasswordHasher(),
        )
        current_session = service.authenticate("admin", TEST_PASSWORD)
        session.commit()

    assert current_session.username == "admin"
    assert current_session.rol_codigo == "ADMIN"
    assert "usuarios.gestionar" in current_session.permisos


def test_authentication_rejects_invalid_password(
    tmp_path: Path,
    project_root: Path,
) -> None:
    session_factory = _build_session_factory(tmp_path, project_root)
    _seed_admin(session_factory)

    with session_factory() as session:
        service = AuthenticationService(
            user_repository=SqlAlchemyUserRepository(session),
            configuration_repository=SqlAlchemyConfigurationRepository(session),
            password_hasher=Argon2PasswordHasher(),
        )
        with pytest.raises(ValidationError, match="incorrectos"):
            service.authenticate("admin", "no-es-la-clave")


def test_change_password_updates_hash_and_clears_flag(
    tmp_path: Path,
    project_root: Path,
) -> None:
    session_factory = _build_session_factory(tmp_path, project_root)
    _seed_admin(session_factory)
    _mark_password_change_required(session_factory)

    with session_factory() as session:
        service = ChangePasswordService(
            user_repository=SqlAlchemyUserRepository(session),
            configuration_repository=SqlAlchemyConfigurationRepository(session),
            password_hasher=Argon2PasswordHasher(),
        )
        service.change_password(
            user_id=_require_admin_id(session),
            current_password=TEST_PASSWORD,
            new_password="NuevaClave123",  # noqa: S106
            confirm_password="NuevaClave123",  # noqa: S106
        )
        session.commit()

    with session_factory() as session:
        auth_service = AuthenticationService(
            user_repository=SqlAlchemyUserRepository(session),
            configuration_repository=SqlAlchemyConfigurationRepository(session),
            password_hasher=Argon2PasswordHasher(),
        )
        current_session = auth_service.authenticate("admin", "NuevaClave123")

    assert current_session.debe_cambiar_password is False

    with session_factory() as session:
        auth_service = AuthenticationService(
            user_repository=SqlAlchemyUserRepository(session),
            configuration_repository=SqlAlchemyConfigurationRepository(session),
            password_hasher=Argon2PasswordHasher(),
        )
        with pytest.raises(ValidationError, match="incorrectos"):
            auth_service.authenticate("admin", TEST_PASSWORD)


def test_change_password_rejects_incorrect_current_password(
    tmp_path: Path,
    project_root: Path,
) -> None:
    session_factory = _build_session_factory(tmp_path, project_root)
    _seed_admin(session_factory)

    with session_factory() as session:
        service = ChangePasswordService(
            user_repository=SqlAlchemyUserRepository(session),
            configuration_repository=SqlAlchemyConfigurationRepository(session),
            password_hasher=Argon2PasswordHasher(),
        )
        with pytest.raises(ValidationError, match="actual es incorrecta"):
            service.change_password(
                user_id=_require_admin_id(session),
                current_password="incorrecta",  # noqa: S106
                new_password="NuevaClave123",  # noqa: S106
                confirm_password="NuevaClave123",  # noqa: S106
            )


def test_authorization_service_denies_missing_permission() -> None:
    service = AuthorizationService()

    with pytest.raises(PermissionDenied, match="No tiene permiso"):
        service.require_permission(
            session=_build_current_session({"productos.ver"}),
            permission_code="usuarios.gestionar",
        )


def test_authorization_service_accepts_existing_permission() -> None:
    service = AuthorizationService()

    service.require_permission(
        session=_build_current_session({"usuarios.gestionar", "productos.ver"}),
        permission_code="usuarios.gestionar",
    )


def test_user_management_creates_user_with_temporary_password(
    tmp_path: Path,
    project_root: Path,
) -> None:
    session_factory = _build_session_factory(tmp_path, project_root)
    _seed_admin(session_factory)
    current_session = _login_as_admin(session_factory)

    with session_factory() as session:
        service = UserManagementService(
            user_repository=SqlAlchemyUserRepository(session),
            configuration_repository=SqlAlchemyConfigurationRepository(session),
            password_hasher=Argon2PasswordHasher(),
        )
        created = service.create_user(
            current_session,
            CreateUserPayload(
                username="operador1",
                nombre_completo="Operador Uno",
                rol_codigo="OPERADOR",
                password="Temporal123",  # noqa: S106
                confirm_password="Temporal123",  # noqa: S106
            ),
        )
        session.commit()

    assert created.id is not None
    assert created.debe_cambiar_password is True

    with session_factory() as session:
        auth_service = AuthenticationService(
            user_repository=SqlAlchemyUserRepository(session),
            configuration_repository=SqlAlchemyConfigurationRepository(session),
            password_hasher=Argon2PasswordHasher(),
        )
        current_user = auth_service.authenticate("operador1", "Temporal123")

    assert current_user.rol_codigo == "OPERADOR"
    assert current_user.debe_cambiar_password is True


def test_user_management_rejects_missing_permission(
    tmp_path: Path,
    project_root: Path,
) -> None:
    session_factory = _build_session_factory(tmp_path, project_root)
    _seed_admin(session_factory)

    with session_factory() as session:
        service = UserManagementService(
            user_repository=SqlAlchemyUserRepository(session),
            configuration_repository=SqlAlchemyConfigurationRepository(session),
            password_hasher=Argon2PasswordHasher(),
        )
        with pytest.raises(PermissionDenied, match="No tiene permiso"):
            service.list_users(_build_current_session({"productos.ver"}))


def test_user_management_rejects_self_deactivation(
    tmp_path: Path,
    project_root: Path,
) -> None:
    session_factory = _build_session_factory(tmp_path, project_root)
    _seed_admin(session_factory)
    current_session = _login_as_admin(session_factory)

    with session_factory() as session:
        service = UserManagementService(
            user_repository=SqlAlchemyUserRepository(session),
            configuration_repository=SqlAlchemyConfigurationRepository(session),
            password_hasher=Argon2PasswordHasher(),
        )
        with pytest.raises(BusinessRuleViolation, match="propio usuario"):
            service.update_user(
                current_session,
                UpdateUserPayload(
                    user_id=current_session.user_id,
                    username="admin",
                    nombre_completo="Administrador General",
                    rol_codigo="ADMIN",
                    activo=False,
                ),
            )


def test_user_management_rejects_deactivating_last_admin(
    tmp_path: Path,
    project_root: Path,
) -> None:
    session_factory = _build_session_factory(tmp_path, project_root)
    _seed_admin(session_factory)

    with session_factory() as session:
        service = UserManagementService(
            user_repository=SqlAlchemyUserRepository(session),
            configuration_repository=SqlAlchemyConfigurationRepository(session),
            password_hasher=Argon2PasswordHasher(),
        )
        with pytest.raises(BusinessRuleViolation, match="último administrador activo"):
            service.update_user(
                _build_current_session({"usuarios.gestionar"}, user_id=999),
                UpdateUserPayload(
                    user_id=_require_admin_id(session),
                    username="admin",
                    nombre_completo="Administrador General",
                    rol_codigo="ADMIN",
                    activo=False,
                ),
            )


def test_user_management_reset_password_forces_change_and_unlocks(
    tmp_path: Path,
    project_root: Path,
) -> None:
    session_factory = _build_session_factory(tmp_path, project_root)
    _seed_admin(session_factory)
    current_session = _login_as_admin(session_factory)
    user_id = _create_operator(session_factory, current_session)
    _lock_user(session_factory, user_id)

    with session_factory() as session:
        service = UserManagementService(
            user_repository=SqlAlchemyUserRepository(session),
            configuration_repository=SqlAlchemyConfigurationRepository(session),
            password_hasher=Argon2PasswordHasher(),
        )
        service.reset_password(
            current_session,
            ResetUserPasswordPayload(
                user_id=user_id,
                password="NuevaTemporal123",  # noqa: S106
                confirm_password="NuevaTemporal123",  # noqa: S106
            ),
        )
        session.commit()

    with session_factory() as session:
        auth_service = AuthenticationService(
            user_repository=SqlAlchemyUserRepository(session),
            configuration_repository=SqlAlchemyConfigurationRepository(session),
            password_hasher=Argon2PasswordHasher(),
        )
        current_user = auth_service.authenticate("operador1", "NuevaTemporal123")

    assert current_user.debe_cambiar_password is True


def _seed_admin(session_factory: sessionmaker[Session]) -> None:
    with session_factory() as session:
        service = InitialSetupService(
            user_repository=SqlAlchemyUserRepository(session),
            configuration_repository=SqlAlchemyConfigurationRepository(session),
            password_hasher=Argon2PasswordHasher(),
        )
        service.create_initial_admin(
            InitialAdminPayload(
                empresa_nombre="Almacén Central",
                backup_carpeta="",
                username="admin",
                nombre_completo="Administrador General",
                password=TEST_PASSWORD,  # noqa: S106
                confirm_password=TEST_PASSWORD,  # noqa: S106
            )
        )
        session.commit()


def _create_operator(
    session_factory: sessionmaker[Session],
    current_session: CurrentSession,
) -> int:
    with session_factory() as session:
        service = UserManagementService(
            user_repository=SqlAlchemyUserRepository(session),
            configuration_repository=SqlAlchemyConfigurationRepository(session),
            password_hasher=Argon2PasswordHasher(),
        )
        user = service.create_user(
            current_session,
            CreateUserPayload(
                username="operador1",
                nombre_completo="Operador Uno",
                rol_codigo="OPERADOR",
                password="Temporal123",  # noqa: S106
                confirm_password="Temporal123",  # noqa: S106
            ),
        )
        session.commit()
    assert user.id is not None
    return user.id


def _lock_user(session_factory: sessionmaker[Session], user_id: int) -> None:
    with session_factory() as session:
        user = session.get(Usuario, user_id)
        assert user is not None
        user.intentos_fallidos = 4
        user.bloqueado_hasta = "2099-01-01T00:00:00Z"
        session.commit()


def _mark_password_change_required(session_factory: sessionmaker[Session]) -> None:
    with session_factory() as session:
        admin_user = session.execute(
            select(Usuario).where(Usuario.username == "admin")
        ).scalar_one()
        admin_user.debe_cambiar_password = 1
        session.commit()


def _require_admin_id(session: Session) -> int:
    admin_id = session.execute(select(Usuario.id).where(Usuario.username == "admin")).scalar_one()
    return int(admin_id)


def _login_as_admin(session_factory: sessionmaker[Session]) -> CurrentSession:
    with session_factory() as session:
        service = AuthenticationService(
            user_repository=SqlAlchemyUserRepository(session),
            configuration_repository=SqlAlchemyConfigurationRepository(session),
            password_hasher=Argon2PasswordHasher(),
        )
        return service.authenticate("admin", TEST_PASSWORD)


def _build_current_session(
    permissions: set[str],
    *,
    user_id: int = 1,
) -> CurrentSession:
    return CurrentSession(
        user_id=user_id,
        username="admin",
        nombre_completo="Administrador General",
        rol_codigo="ADMIN",
        rol_nombre="Administrador",
        permisos=permissions,
        debe_cambiar_password=False,
    )


def _build_session_factory(
    tmp_path: Path,
    project_root: Path,
) -> sessionmaker[Session]:
    database_path = tmp_path / "auth.sqlite3"
    run_migrations(database_path=database_path, project_root=project_root)
    engine = create_sqlite_engine(database_path)
    return create_session_factory(engine)
