# Community Labeling

Graphify is running in assistant/skill mode (no API key). You are the host
assistant (Claude Code / Codex / Gemini CLI). Read the community listing below
and write 2-5 word plain-language names for each.

## Language

LANGUAGE: each community line ends with a `[lang=…]` marker giving the
language of its source nodes. Write that community's name in EXACTLY that
language. Do not normalize every name to one common language.

## Communities

Community 0: BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError, auth.py, AuthenticationService, .authenticate(, .__init__(, AuthorizationService, .require_permission(, ChangePasswordService [lang=en]
Community 1: SqlAlchemyUserRepository, Base, ScaledMoney, ScaledQuantity, ConfigurationRepository, DashboardRepository, auth_repositories.py, _count(, _map_auth_user(, _map_user_summary(, Repositorios de autenticación y resumen inicial., Configuración persistida sobre SQLite. [lang=en]
Community 2: MainWindow, CurrentSession, initial_setup_dialog.py, InitialSetupDialog, .__init__(, ._setup_ui(, ._submit(, .suggested_username(, Asistente de primer arranque., Devuelve el usuario ingresado, útil para prefijar el login., Solicita los datos básicos del primer administrador., login_dialog.py [lang=es]
Community 3: auth.py, AuthUser, ConfigurationRepository, .get_many(, .set_many(, DashboardRepository, .get_snapshot(, DashboardSnapshot, Modelos y puertos para autenticación y estado inicial., Lista permisos asignados a un rol., Puerto para configuración persistente., Obtiene varias claves de configuración. [lang=es]
Community 4: 001_schema.sql, auditoria, categoria, configuracion, detalle_importacion, detalle_movimiento, importacion, inventario, marca, movimiento, permiso, producto [lang=en]
Community 5: ABC, uow.py, Contrato de unidad de trabajo para casos de uso., Confirma la transacción activa., Revierte la transacción activa., Unidad de trabajo abstracta para coordinar transacciones., UnitOfWork, .commit(, .__enter__(, .__exit__(, .rollback(, Unidad de trabajo basada en SQLAlchemy. [lang=nl]
Community 6: test_auth_services.py, _build_current_session(, _build_session_factory(, _create_operator(, _lock_user(, _login_as_admin(, _mark_password_change_required(, _require_admin_id(, _seed_admin(, test_authentication_accepts_valid_credentials(, test_authentication_rejects_invalid_password(, test_authorization_service_accepts_existing_permission( [lang=en]
Community 7: repositories.py, Repositorios base sobre SQLAlchemy., Implementación mínima de repositorio para la Entrega 0., SqlAlchemyRepository, .add(, .get_by_id(, .__init__(, Protocolos base de repositorios del dominio., Contrato mínimo para repositorios inyectables., Agrega una entidad a la unidad de trabajo., Obtiene una entidad por su identificador., Repository [lang=es]
Community 8: config.py, AppPaths, Resolución de rutas y configuración base de la aplicación., Rutas utilizadas por la aplicación local., Obtiene la raíz del proyecto en modo desarrollo., Construye las rutas persistentes principales., resolve_app_paths(, resolve_project_root(, bootstrap.py, AppContext, bootstrap_application(, Bootstrap principal de la aplicación. [lang=es]
Community 9: bootstrap.py, _bootstrap_sql_files(, build_alembic_config(, _database_has_tables(, Inicialización de la base de datos y migraciones., Resuelve la ruta real de archivos de recursos tanto en desar, Construye la configuración de Alembic para una base destino., Comprueba si la base ya contiene tablas creadas., Crea la Base de Datos desde los SQL de referencia cuando no , Aplica todas las migraciones pendientes a la base indicada., _resolve_runtime_path(, run_migrations( [lang=es]
Community 10: 0001_initial.py, downgrade(, Migración inicial equivalente al SQL de referencia., _repo_root(, _run_script(, _sqlite_connection(, upgrade( [lang=nl]
Community 11: session.py, create_session_factory(, create_sqlite_engine(, Creación de engine y sesiones SQLite., Crea un engine SQLite con las pragmas obligatorias., Construye la factoría de sesiones usada por la aplicación. [lang=es]
Community 12: test_schema_reference.py, _execute_script(, Pruebas de equivalencia entre la migración y el SQL de refer, _schema_snapshot(, test_initial_migration_loads_seed_data(, test_initial_migration_matches_reference_schema( [lang=es]
Community 13: env.py, Entorno Alembic para SisAlmacen., Ejecuta migraciones en modo offline., Ejecuta migraciones en modo online., run_migrations_offline(, run_migrations_online( [lang=es]
Community 14: logging.py, configure_logging(, Configuración de logging de SisAlmacen., Configura logging rotativo sin exponer datos sensibles. [lang=nl]
Community 15: test_uow.py, Pruebas mínimas de la unidad de trabajo., test_sqlalchemy_uow_commit_persists_changes(, test_sqlalchemy_uow_rollback_discards_changes( [lang=nl]
Community 16: theme.py, get_brand_style_sheet(, Tema visual corporativo para la aplicación de Grupo Corporac, Devuelve la hoja de estilo con identidad industrial del logo [lang=es]
Community 17: test_brand_theme.py, Pruebas del branding corporativo de la aplicación., test_brand_palette_has_company_colors(, test_brand_stylesheet_contains_expected_sections( [lang=en]
Community 18: conftest.py, project_root(, Fixtures compartidas de pruebas. [lang=nl]
Community 19: __init__.py, Capa de aplicación de SisAlmacen. [lang=nl]
Community 20: __init__.py, Infraestructura de base de datos. [lang=nl]
Community 21: __init__.py, Diálogos de la interfaz principal. [lang=en]
Community 22: __init__.py, Capa de dominio de SisAlmacen. [lang=nl]
Community 23: __init__.py, Infraestructura de SisAlmacen. [lang=nl]
Community 24: __init__.py, Servicios de seguridad. [lang=nl]
Community 25: __init__.py, Paquete principal de SisAlmacen. [lang=nl]
Community 26: __init__.py, Interfaz de usuario de SisAlmacen. [lang=nl]
Community 27: 002_seed.sql [lang=en]

## Instructions

Write a single JSON object mapping each community id (as a string) to its
2-5 word name to: c:\Users\friveraq\Downloads\SisAlmacen 1 (1)\SisAlmacen\SisAlmacen\.graphify\label-instructions\communities.json

Example:
```json
{
  "0": "Authentication Flow",
  "1": "Authentication Flow",
  "2": "Authentication Flow"
}
```

Then re-run `graphify update` (or `graphify label`) to ingest the names.
