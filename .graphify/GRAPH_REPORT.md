# Graph Report - .  (2026-10-03)

## Corpus Check
- Corpus is ~12,194 words - fits in a single context window. You may not need a graph.

## Summary
- 420 nodes · 919 edges · 27 communities detected
- Extraction: 59% EXTRACTED · 41% INFERRED · 0% AMBIGUOUS · INFERRED: 379 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output
- Edge kinds: uses: 379 · contains: 149 · rationale_for: 120 · calls: 102 · method: 100 · inherits: 38 · references: 20 · triggers: 8 · imports_from: 2 · reads_from: 1


## Input Scope
- Requested: all
- Resolved: all (source: configured-default)
- Included files: 44 · Candidates: recursive
- Excluded: 0 untracked · 0 ignored · 1 sensitive · 0 missing committed
## God Nodes (most connected - your core abstractions)
1. `ValidationError` - 39 edges
2. `PermissionDenied` - 39 edges
3. `BusinessRuleViolation` - 39 edges
4. `NotFoundError` - 38 edges
5. `ConflictError` - 38 edges
6. `SqlAlchemyUserRepository` - 28 edges
7. `Base` - 28 edges
8. `ScaledQuantity` - 24 edges
9. `ScaledMoney` - 24 edges
10. `MainWindow` - 21 edges

## Surprising Connections (you probably didn't know these)
- `Pruebas mínimas de la unidad de trabajo.` --uses--> `Configuracion`  [INFERRED]
  tests/integration/test_uow.py → src/sisalmacen/infrastructure/db/models.py
- `Pruebas de primer arranque y autenticación.` --uses--> `CurrentSession`  [INFERRED]
  tests/integration/test_auth_services.py → src/sisalmacen/application/auth.py
- `Pruebas de primer arranque y autenticación.` --uses--> `SqlAlchemyConfigurationRepository`  [INFERRED]
  tests/integration/test_auth_services.py → src/sisalmacen/infrastructure/db/auth_repositories.py
- `Pruebas de primer arranque y autenticación.` --uses--> `SqlAlchemyUserRepository`  [INFERRED]
  tests/integration/test_auth_services.py → src/sisalmacen/infrastructure/db/auth_repositories.py
- `Pruebas de primer arranque y autenticación.` --uses--> `Configuracion`  [INFERRED]
  tests/integration/test_auth_services.py → src/sisalmacen/infrastructure/db/models.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.10
Nodes (46): AuthenticationService, AuthorizationService, ChangePasswordService, CreateUserPayload, DashboardService, _format_utc(), InitialAdminPayload, InitialSetupService (+38 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (45): Base, ConfigurationRepository, DashboardRepository, _count(), _map_auth_user(), _map_user_summary(), Repositorios de autenticación y resumen inicial., Configuración persistida sobre SQLite. (+37 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (28): CurrentSession, InitialSetupDialog, Asistente de primer arranque., Devuelve el usuario ingresado, útil para prefijar el login., Solicita los datos básicos del primer administrador., LoginDialog, Diálogo de autenticación local., Solicita credenciales para ingresar al sistema. (+20 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (30): AuthUser, ConfigurationRepository, DashboardRepository, DashboardSnapshot, Modelos y puertos para autenticación y estado inicial., Lista permisos asignados a un rol., Puerto para configuración persistente., Obtiene varias claves de configuración. (+22 more)

### Community 4 - "Community 4"
Cohesion: 0.16
Nodes (26): auditoria, categoria, configuracion, detalle_importacion, detalle_movimiento, importacion, inventario, marca (+18 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (10): ABC, Contrato de unidad de trabajo para casos de uso., Confirma la transacción activa., Revierte la transacción activa., Unidad de trabajo abstracta para coordinar transacciones., UnitOfWork, Unidad de trabajo basada en SQLAlchemy., Implementación concreta de la unidad de trabajo. (+2 more)

### Community 6 - "Community 6"
Cohesion: 0.25
Nodes (20): _build_current_session(), _build_session_factory(), _create_operator(), _lock_user(), _login_as_admin(), _mark_password_change_required(), _require_admin_id(), _seed_admin() (+12 more)

### Community 7 - "Community 7"
Cohesion: 0.15
Nodes (8): Repositorios base sobre SQLAlchemy., Implementación mínima de repositorio para la Entrega 0., SqlAlchemyRepository, Protocolos base de repositorios del dominio., Contrato mínimo para repositorios inyectables., Agrega una entidad a la unidad de trabajo., Obtiene una entidad por su identificador., Repository

### Community 8 - "Community 8"
Cohesion: 0.21
Nodes (12): AppPaths, Resolución de rutas y configuración base de la aplicación., Rutas utilizadas por la aplicación local., Obtiene la raíz del proyecto en modo desarrollo., Construye las rutas persistentes principales., resolve_app_paths(), resolve_project_root(), AppContext (+4 more)

### Community 9 - "Community 9"
Cohesion: 0.27
Nodes (11): _bootstrap_sql_files(), build_alembic_config(), _database_has_tables(), Inicialización de la base de datos y migraciones., Resuelve la ruta real de archivos de recursos tanto en desarrollo como empaqueta, Construye la configuración de Alembic para una base destino., Comprueba si la base ya contiene tablas creadas., Crea la Base de Datos desde los SQL de referencia cuando no hay migración dispon (+3 more)

### Community 10 - "Community 10"
Cohesion: 0.43
Nodes (5): Migración inicial equivalente al SQL de referencia., _repo_root(), _run_script(), _sqlite_connection(), upgrade()

### Community 11 - "Community 11"
Cohesion: 0.33
Nodes (5): create_session_factory(), create_sqlite_engine(), Creación de engine y sesiones SQLite., Crea un engine SQLite con las pragmas obligatorias., Construye la factoría de sesiones usada por la aplicación.

### Community 12 - "Community 12"
Cohesion: 0.47
Nodes (4): _execute_script(), Pruebas de equivalencia entre la migración y el SQL de referencia., _schema_snapshot(), test_initial_migration_matches_reference_schema()

### Community 13 - "Community 13"
Cohesion: 0.33
Nodes (5): Entorno Alembic para SisAlmacen., Ejecuta migraciones en modo offline., Ejecuta migraciones en modo online., run_migrations_offline(), run_migrations_online()

### Community 14 - "Community 14"
Cohesion: 0.50
Nodes (3): configure_logging(), Configuración de logging de SisAlmacen., Configura logging rotativo sin exponer datos sensibles.

### Community 15 - "Community 15"
Cohesion: 0.50
Nodes (1): Pruebas mínimas de la unidad de trabajo.

### Community 16 - "Community 16"
Cohesion: 0.50
Nodes (3): get_brand_style_sheet(), Tema visual corporativo para la aplicación de Grupo Corporación., Devuelve la hoja de estilo con identidad industrial del logo de la empresa.

### Community 17 - "Community 17"
Cohesion: 0.50
Nodes (1): Pruebas del branding corporativo de la aplicación.

### Community 18 - "Community 18"
Cohesion: 0.67
Nodes (1): Fixtures compartidas de pruebas.

### Community 19 - "Community 19"
Cohesion: 1.00
Nodes (1): Capa de aplicación de SisAlmacen.

### Community 20 - "Community 20"
Cohesion: 1.00
Nodes (1): Infraestructura de base de datos.

### Community 21 - "Community 21"
Cohesion: 1.00
Nodes (1): Diálogos de la interfaz principal.

### Community 22 - "Community 22"
Cohesion: 1.00
Nodes (1): Capa de dominio de SisAlmacen.

### Community 23 - "Community 23"
Cohesion: 1.00
Nodes (1): Infraestructura de SisAlmacen.

### Community 24 - "Community 24"
Cohesion: 1.00
Nodes (1): Servicios de seguridad.

### Community 25 - "Community 25"
Cohesion: 1.00
Nodes (1): Paquete principal de SisAlmacen.

### Community 26 - "Community 26"
Cohesion: 1.00
Nodes (1): Interfaz de usuario de SisAlmacen.

## Knowledge Gaps
- **68 isolated node(s):** `configuracion`, `Migración inicial equivalente al SQL de referencia.`, `Paquete principal de SisAlmacen.`, `Capa de aplicación de SisAlmacen.`, `Contrato de unidad de trabajo para casos de uso.` (+63 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 15`** (1 nodes): `Pruebas mínimas de la unidad de trabajo.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (1 nodes): `Pruebas del branding corporativo de la aplicación.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (1 nodes): `Fixtures compartidas de pruebas.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `Capa de aplicación de SisAlmacen.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `Infraestructura de base de datos.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `Diálogos de la interfaz principal.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `Capa de dominio de SisAlmacen.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `Infraestructura de SisAlmacen.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `Servicios de seguridad.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `Paquete principal de SisAlmacen.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `Interfaz de usuario de SisAlmacen.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Pruebas de primer arranque y autenticación.` connect `Community 0` to `Community 2`, `Community 1`, `Community 6`?**
  _High betweenness centrality (0.168) - this node is a cross-community bridge._
- **Why does `Base` connect `Community 1` to `Community 7`, `Community 13`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Why does `Punto de entrada de SisAlmacen.` connect `Community 2` to `Community 0`, `Community 1`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `ValidationError` (e.g. with `AuthenticationService` and `AuthorizationService`) actually correct?**
  _`ValidationError` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 37 inferred relationships involving `PermissionDenied` (e.g. with `AuthenticationService` and `AuthorizationService`) actually correct?**
  _`PermissionDenied` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 37 inferred relationships involving `BusinessRuleViolation` (e.g. with `AuthenticationService` and `AuthorizationService`) actually correct?**
  _`BusinessRuleViolation` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 36 inferred relationships involving `NotFoundError` (e.g. with `AuthenticationService` and `AuthorizationService`) actually correct?**
  _`NotFoundError` has 36 INFERRED edges - model-reasoned connections that need verification._