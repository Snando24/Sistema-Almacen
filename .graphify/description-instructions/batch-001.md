# Node Description Batch 2 of 11

Graphify is running in assistant/skill mode (no API key). You are the host
assistant (Claude Code / Codex / Gemini CLI). Read the prompt below and write
your JSON answer to the answer file.

## Prompt

You are documenting nodes in a knowledge graph.
For each entry below, write ONE concise factual plain-language sentence
describing what it is or does. Use only the provided context.
For a code symbol (kind=code-symbol — a function, class, or constant),
describe what the function/symbol does based on its name, source location
and neighbors — e.g. "Resolves the configured ontology profile from graphify.yaml.".
For an entity node (any other kind — e.g. a person, place, event, object),
describe what the entity is and its role, grounded in its type, its
relations (neighbors) and the provided citations/evidence — e.g.
"Lady Carfax, a wealthy heiress who disappears en route to Lausanne.".
Ground entity descriptions in the citations/evidence when present; do not
speculate beyond the context, so a node with no supporting context may be
left out of the reply.
LANGUAGE: each entry has a `lang=` marker giving the language of its source.
Write that entry's description in EXACTLY that language. Do not translate to
a single common language — match each node's source language individually.
No marketing language.
Respond ONLY with a JSON object mapping each node id (as a string) to its
one-sentence description — no prose, no markdown fences.

- "integration_test_auth_services_build_session_factory": "_build_session_factory()" | kind=code-symbol | source=tests/integration/test_auth_services.py:L441 | neighbors=[test_auth_services.py, test_authentication_accepts_valid_crede…, test_authentication_rejects_invalid_pas…, test_change_password_rejects_incorrect_…, test_change_password_updates_hash_and_c…, test_initial_setup_creates_admin_and_co…] | lang=en
- "application_auth_authorizationservice": "AuthorizationService" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L344 | neighbors=[auth.py, .require_permission(), BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied] | lang=en
- "application_uow_unitofwork": "UnitOfWork" | kind=code-symbol | source=src/sisalmacen/application/uow.py:L8 | neighbors=[uow.py, Unidad de trabajo abstracta para coordi…, ABC, .commit(), .__enter__(), .__exit__()] | lang=en
- "db_001_schema_producto": "producto" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L101 | neighbors=[001_schema.sql, detalle_movimiento, inventario, categoria, marca, proveedor] | lang=en
- "db_auth_repositories_rationale_1": "Repositorios de autenticación y resumen inicial." | kind=entity | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L1 | neighbors=[auth_repositories.py, Categoria, Configuracion, Movimiento, Permiso, Producto] | lang=en
- "db_auth_repositories_rationale_157": "Configuración persistida sobre SQLite." | kind=entity | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L157 | neighbors=[SqlAlchemyConfigurationRepository, Categoria, Configuracion, Movimiento, Permiso, Producto] | lang=en
- "db_auth_repositories_rationale_180": "Resumen inicial mostrado en la aplicación." | kind=entity | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L180 | neighbors=[SqlAlchemyDashboardRepository, Categoria, Configuracion, Movimiento, Permiso, Producto] | lang=es
- "db_auth_repositories_rationale_33": "Implementación SQLAlchemy para autenticación." | kind=entity | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L33 | neighbors=[SqlAlchemyUserRepository, Categoria, Configuracion, Movimiento, Permiso, Producto] | lang=en
- "integration_test_auth_services_seed_admin": "_seed_admin()" | kind=code-symbol | source=tests/integration/test_auth_services.py:L347 | neighbors=[test_auth_services.py, test_authentication_accepts_valid_crede…, test_authentication_rejects_invalid_pas…, test_change_password_rejects_incorrect_…, test_change_password_updates_hash_and_c…, test_user_management_creates_user_with_…] | lang=en
- "application_auth_passwordhasherport": "PasswordHasherPort" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L85 | neighbors=[auth.py, .hash(), .verify(), BusinessRuleViolation, ConflictError, NotFoundError] | lang=en
- "db_001_schema_movimiento": "movimiento" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L185 | neighbors=[001_schema.sql, detalle_movimiento, importacion, movimiento, tipo_movimiento, usuario] | lang=en
- "db_uow_sqlalchemyunitofwork": "SqlAlchemyUnitOfWork" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/uow.py:L10 | neighbors=[uow.py, Implementación concreta de la unidad de…, UnitOfWork, .commit(), .__enter__(), .__exit__()] | lang=en
- "application_auth_authenticationservice_authenticate": ".authenticate()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L210 | neighbors=[AuthenticationService, CurrentSession, _format_utc(), _parse_utc(), .verify(), _require_user_id()] | lang=en
- "application_auth_createuserpayload": "CreateUserPayload" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L52 | neighbors=[auth.py, BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError] | lang=en
- "application_auth_resetuserpasswordpayload": "ResetUserPasswordPayload" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L76 | neighbors=[auth.py, Datos para reinicio administrativo de c…, BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied] | lang=en
- "application_auth_updateuserpayload": "UpdateUserPayload" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L65 | neighbors=[auth.py, Datos editables de un usuario existente., BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied] | lang=en
- "domain_auth": "auth.py" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L1 | neighbors=[AuthUser, ConfigurationRepository, DashboardRepository, DashboardSnapshot, RoleInfo, UserRepository] | lang=en
- "application_auth_authorizationservice_require_permission": ".require_permission()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L347 | neighbors=[AuthorizationService, Exige un permiso específico y falla con…, .create_user(), .list_roles(), .list_users(), .reset_password()] | lang=en
- "application_auth_usermanagementservice_update_user": ".update_user()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L428 | neighbors=[Actualiza datos básicos, rol y estado l…, UserManagementService, .require_permission(), ._ensure_username_available(), ._require_role(), ._require_user()] | lang=en
- "db_auth_repositories": "auth_repositories.py" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L1 | neighbors=[_count(), _map_auth_user(), _map_user_summary(), SqlAlchemyConfigurationRepository, SqlAlchemyDashboardRepository, SqlAlchemyUserRepository] | lang=en
- "db_repositories_sqlalchemyrepository": "SqlAlchemyRepository" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/repositories.py:L16 | neighbors=[repositories.py, Implementación mínima de repositorio pa…, Base, .add(), .get_by_id(), .__init__()] | lang=en
- "db_types_scaleddecimal": "ScaledDecimal" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/types.py:L11 | neighbors=[types.py, Persiste decimales como enteros escalad…, .__init__(), .process_bind_param(), .process_result_value(), ScaledMoney] | lang=en
- "domain_errors": "errors.py" | kind=code-symbol | source=src/sisalmacen/domain/errors.py:L1 | neighbors=[BusinessRuleViolation, ConflictError, DomainError, NotFoundError, PermissionDenied, ValidationError] | lang=en
- "domain_repositories_repository": "Repository" | kind=code-symbol | source=src/sisalmacen/domain/repositories.py:L11 | neighbors=[Repositorios base sobre SQLAlchemy., Implementación mínima de repositorio pa…, SqlAlchemyRepository, repositories.py, Contrato mínimo para repositorios inyec…, .add()] | lang=en
- "infrastructure_config_apppaths": "AppPaths" | kind=code-symbol | source=src/sisalmacen/infrastructure/config.py:L10 | neighbors=[config.py, Rutas utilizadas por la aplicación loca…, resolve_app_paths(), AppContext, Bootstrap principal de la aplicación., Dependencias principales de ejecución.] | lang=en
- "sisalmacen_main": "main.py" | kind=code-symbol | source=src/sisalmacen/main.py:L1 | neighbors=[bootstrap.py, _build_dashboard_loader(), _build_initial_setup_handler(), _build_login_handler(), main(), _requires_initial_setup()] | lang=en
- "application_auth_rationale_1": "Casos de uso de autenticación y primer arranque." | kind=entity | source=src/sisalmacen/application/auth.py:L1 | neighbors=[auth.py, BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError] | lang=nl
- "application_auth_rationale_111": "Indica si aún no existe ningún usuario." | kind=entity | source=src/sisalmacen/application/auth.py:L111 | neighbors=[.requires_initial_setup(), BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError] | lang=pt
- "application_auth_rationale_116": "Crea el primer usuario ADMIN y la configuración básica." | kind=entity | source=src/sisalmacen/application/auth.py:L116 | neighbors=[.create_initial_admin(), BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError] | lang=es
- "application_auth_rationale_196": "Valida credenciales y construye la sesión del usuario." | kind=entity | source=src/sisalmacen/application/auth.py:L196 | neighbors=[AuthenticationService, BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError] | lang=es
- "application_auth_rationale_211": "Autentica un usuario y actualiza el estado de acceso." | kind=entity | source=src/sisalmacen/application/auth.py:L211 | neighbors=[.authenticate(), BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError] | lang=es
- "application_auth_rationale_275": "Gestiona el cambio de contraseña del usuario autenticado." | kind=entity | source=src/sisalmacen/application/auth.py:L275 | neighbors=[ChangePasswordService, BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError] | lang=es
- "application_auth_rationale_28": "Usuario autenticado en la sesión actual." | kind=entity | source=src/sisalmacen/application/auth.py:L28 | neighbors=[CurrentSession, BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError] | lang=es
- "application_auth_rationale_297": "Actualiza la contraseña del usuario y limpia el cambio obligatorio." | kind=entity | source=src/sisalmacen/application/auth.py:L297 | neighbors=[.change_password(), BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError] | lang=es
- "application_auth_rationale_345": "Valida permisos funcionales de la sesión actual." | kind=entity | source=src/sisalmacen/application/auth.py:L345 | neighbors=[AuthorizationService, BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError] | lang=en
- "application_auth_rationale_348": "Exige un permiso específico y falla con código funcional estable." | kind=entity | source=src/sisalmacen/application/auth.py:L348 | neighbors=[.require_permission(), BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError] | lang=es
- "application_auth_rationale_358": "Gestiona usuarios y asignación de roles." | kind=entity | source=src/sisalmacen/application/auth.py:L358 | neighbors=[UserManagementService, BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError] | lang=en
- "application_auth_rationale_376": "Lista roles disponibles para la UI administrativa." | kind=entity | source=src/sisalmacen/application/auth.py:L376 | neighbors=[.list_roles(), BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError] | lang=es
- "application_auth_rationale_382": "Devuelve usuarios registrados ordenados por nombre de acceso." | kind=entity | source=src/sisalmacen/application/auth.py:L382 | neighbors=[.list_users(), BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError] | lang=en
- "application_auth_rationale_388": "Crea un usuario con contraseña temporal o definitiva." | kind=entity | source=src/sisalmacen/application/auth.py:L388 | neighbors=[.create_user(), BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError] | lang=es

## Instructions

Write a single JSON object mapping each node id to a one-sentence description
to: c:\Users\friveraq\Downloads\SisAlmacen 1 (1)\SisAlmacen\SisAlmacen\.graphify\description-instructions\batch-001.json

Keep each description factual and concise (one sentence). No markdown, no prose
outside the JSON object. It is acceptable to omit a node if context is
insufficient — but include every node you can ground confidently.

Example answer format:
```json
{
  "node_id_1": "Resolves the configured ontology profile from graphify.yaml.",
  "node_id_2": "Colonel James Barclay, an antagonist in The Crooked Man."
}
```
