# Node Description Batch 1 of 11

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
Write every description in Dutch (nl). Do not switch languages.
No marketing language.
Respond ONLY with a JSON object mapping each node id (as a string) to its
one-sentence description — no prose, no markdown fences.

- "domain_errors_businessruleviolation": "BusinessRuleViolation" | kind=code-symbol | source=src/sisalmacen/domain/errors.py:L33 | neighbors=[AuthenticationService, AuthorizationService, ChangePasswordService, CreateUserPayload, CurrentSession, DashboardService]
- "domain_errors_permissiondenied": "PermissionDenied" | kind=code-symbol | source=src/sisalmacen/domain/errors.py:L21 | neighbors=[AuthenticationService, AuthorizationService, ChangePasswordService, CreateUserPayload, CurrentSession, DashboardService]
- "domain_errors_validationerror": "ValidationError" | kind=code-symbol | source=src/sisalmacen/domain/errors.py:L17 | neighbors=[AuthenticationService, AuthorizationService, ChangePasswordService, CreateUserPayload, CurrentSession, DashboardService]
- "domain_errors_conflicterror": "ConflictError" | kind=code-symbol | source=src/sisalmacen/domain/errors.py:L29 | neighbors=[AuthenticationService, AuthorizationService, ChangePasswordService, CreateUserPayload, CurrentSession, DashboardService]
- "domain_errors_notfounderror": "NotFoundError" | kind=code-symbol | source=src/sisalmacen/domain/errors.py:L25 | neighbors=[AuthenticationService, AuthorizationService, ChangePasswordService, CreateUserPayload, CurrentSession, DashboardService]
- "db_auth_repositories_sqlalchemyuserrepository": "SqlAlchemyUserRepository" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L32 | neighbors=[auth_repositories.py, Implementación SQLAlchemy para autentic…, .add(), .count_active_admins(), .count_active_users(), .count_users()]
- "db_base_base": "Base" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/base.py:L17 | neighbors=[base.py, DeclarativeBase, Base declarativa común para los modelos., Auditoria, Categoria, Configuracion]
- "db_001_schema": "001_schema.sql" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L1 | neighbors=[auditoria, categoria, configuracion, detalle_importacion, detalle_movimiento, importacion]
- "db_types_scaledmoney": "ScaledMoney" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/types.py:L44 | neighbors=[Auditoria, Categoria, Configuracion, DetalleImportacion, DetalleMovimiento, Importacion]
- "db_types_scaledquantity": "ScaledQuantity" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/types.py:L35 | neighbors=[Auditoria, Categoria, Configuracion, DetalleImportacion, DetalleMovimiento, Importacion]
- "integration_test_auth_services": "test_auth_services.py" | kind=code-symbol | source=tests/integration/test_auth_services.py:L1 | neighbors=[_build_current_session(), _build_session_factory(), _create_operator(), _lock_user(), _login_as_admin(), _mark_password_change_required()]
- "ui_main_window_mainwindow": "MainWindow" | kind=code-symbol | source=src/sisalmacen/ui/main_window.py:L31 | neighbors=[Punto de entrada de SisAlmacen., Inicia la aplicación de escritorio., main_window.py, CurrentSession, QMainWindow, ._build_content()]
- "application_auth_usermanagementservice": "UserManagementService" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L357 | neighbors=[auth.py, Gestiona usuarios y asignación de roles., .create_user(), ._ensure_username_available(), ._get_password_min_length(), .__init__()]
- "application_auth_currentsession": "CurrentSession" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L27 | neighbors=[auth.py, .authenticate(), BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied]
- "db_models": "models.py" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/models.py:L1 | neighbors=[Auditoria, Categoria, Configuracion, DetalleImportacion, DetalleMovimiento, Importacion]
- "base": "Base" | kind=code-symbol | neighbors=[Auditoria, Categoria, Configuracion, DetalleImportacion, DetalleMovimiento, Importacion]
- "db_auth_repositories_sqlalchemyconfigurationrepository": "SqlAlchemyConfigurationRepository" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L156 | neighbors=[auth_repositories.py, Configuración persistida sobre SQLite., ConfigurationRepository, .get_many(), .__init__(), .set_many()]
- "integration_test_auth_services_rationale_1": "Pruebas de primer arranque y autenticación." | kind=entity | source=tests/integration/test_auth_services.py:L1 | neighbors=[AuthenticationService, AuthorizationService, ChangePasswordService, CreateUserPayload, CurrentSession, InitialAdminPayload]
- "application_auth": "auth.py" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L1 | neighbors=[AuthenticationService, AuthorizationService, ChangePasswordService, CreateUserPayload, CurrentSession, DashboardService]
- "domain_errors_domainerror": "DomainError" | kind=code-symbol | source=src/sisalmacen/domain/errors.py:L6 | neighbors=[InitialSetupDialog, Asistente de primer arranque., Devuelve el usuario ingresado, útil par…, Solicita los datos básicos del primer a…, LoginDialog, Diálogo de autenticación local.]
- "db_auth_repositories_sqlalchemydashboardrepository": "SqlAlchemyDashboardRepository" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L179 | neighbors=[auth_repositories.py, Resumen inicial mostrado en la aplicaci…, DashboardRepository, .get_snapshot(), .__init__(), Categoria]
- "application_auth_initialadminpayload": "InitialAdminPayload" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L40 | neighbors=[auth.py, BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError]
- "application_auth_initialsetupservice": "InitialSetupService" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L95 | neighbors=[auth.py, .create_initial_admin(), ._get_password_min_length(), .__init__(), .requires_initial_setup(), BusinessRuleViolation]
- "db_models_configuracion": "Configuracion" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/models.py:L16 | neighbors=[Repositorios de autenticación y resumen…, Configuración persistida sobre SQLite., Resumen inicial mostrado en la aplicaci…, Implementación SQLAlchemy para autentic…, SqlAlchemyConfigurationRepository, SqlAlchemyDashboardRepository]
- "domain_auth_userrepository": "UserRepository" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L67 | neighbors=[auth.py, Puerto de lectura y escritura de usuari…, .add(), .count_active_admins(), .count_active_users(), .count_users()]
- "db_models_usuario": "Usuario" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/models.py:L53 | neighbors=[Repositorios de autenticación y resumen…, Configuración persistida sobre SQLite., Resumen inicial mostrado en la aplicaci…, Implementación SQLAlchemy para autentic…, SqlAlchemyConfigurationRepository, SqlAlchemyDashboardRepository]
- "application_auth_authenticationservice": "AuthenticationService" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L195 | neighbors=[auth.py, .authenticate(), .__init__(), BusinessRuleViolation, ConflictError, NotFoundError]
- "db_models_categoria": "Categoria" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/models.py:L75 | neighbors=[Repositorios de autenticación y resumen…, Configuración persistida sobre SQLite., Resumen inicial mostrado en la aplicaci…, Implementación SQLAlchemy para autentic…, SqlAlchemyConfigurationRepository, SqlAlchemyDashboardRepository]
- "db_models_movimiento": "Movimiento" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/models.py:L241 | neighbors=[Repositorios de autenticación y resumen…, Configuración persistida sobre SQLite., Resumen inicial mostrado en la aplicaci…, Implementación SQLAlchemy para autentic…, SqlAlchemyConfigurationRepository, SqlAlchemyDashboardRepository]
- "db_models_permiso": "Permiso" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/models.py:L35 | neighbors=[Repositorios de autenticación y resumen…, Configuración persistida sobre SQLite., Resumen inicial mostrado en la aplicaci…, Implementación SQLAlchemy para autentic…, SqlAlchemyConfigurationRepository, SqlAlchemyDashboardRepository]
- "db_models_producto": "Producto" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/models.py:L135 | neighbors=[Repositorios de autenticación y resumen…, Configuración persistida sobre SQLite., Resumen inicial mostrado en la aplicaci…, Implementación SQLAlchemy para autentic…, SqlAlchemyConfigurationRepository, SqlAlchemyDashboardRepository]
- "db_models_rol": "Rol" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/models.py:L25 | neighbors=[Repositorios de autenticación y resumen…, Configuración persistida sobre SQLite., Resumen inicial mostrado en la aplicaci…, Implementación SQLAlchemy para autentic…, SqlAlchemyConfigurationRepository, SqlAlchemyDashboardRepository]
- "db_models_rolpermiso": "RolPermiso" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/models.py:L43 | neighbors=[Repositorios de autenticación y resumen…, Configuración persistida sobre SQLite., Resumen inicial mostrado en la aplicaci…, Implementación SQLAlchemy para autentic…, SqlAlchemyConfigurationRepository, SqlAlchemyDashboardRepository]
- "db_models_tipomovimiento": "TipoMovimiento" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/models.py:L189 | neighbors=[Repositorios de autenticación y resumen…, Configuración persistida sobre SQLite., Resumen inicial mostrado en la aplicaci…, Implementación SQLAlchemy para autentic…, SqlAlchemyConfigurationRepository, SqlAlchemyDashboardRepository]
- "sisalmacen_main_rationale_1": "Punto de entrada de SisAlmacen." | kind=entity | source=src/sisalmacen/main.py:L1 | neighbors=[AuthenticationService, CurrentSession, DashboardService, InitialAdminPayload, InitialSetupService, SqlAlchemyConfigurationRepository]
- "sisalmacen_main_rationale_34": "Inicia la aplicación de escritorio." | kind=entity | source=src/sisalmacen/main.py:L34 | neighbors=[AuthenticationService, CurrentSession, DashboardService, InitialAdminPayload, InitialSetupService, SqlAlchemyConfigurationRepository]
- "application_auth_changepasswordservice": "ChangePasswordService" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L274 | neighbors=[auth.py, .change_password(), ._get_password_min_length(), .__init__(), BusinessRuleViolation, ConflictError]
- "application_auth_dashboardservice": "DashboardService" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L557 | neighbors=[auth.py, .get_snapshot(), .__init__(), BusinessRuleViolation, ConflictError, NotFoundError]
- "dialogs_initial_setup_dialog_initialsetupdialog": "InitialSetupDialog" | kind=code-symbol | source=src/sisalmacen/ui/dialogs/initial_setup_dialog.py:L26 | neighbors=[initial_setup_dialog.py, InitialAdminPayload, .__init__(), ._setup_ui(), ._submit(), .suggested_username()]
- "dialogs_login_dialog_logindialog": "LoginDialog" | kind=code-symbol | source=src/sisalmacen/ui/dialogs/login_dialog.py:L25 | neighbors=[login_dialog.py, CurrentSession, .__init__(), .session(), ._setup_ui(), ._submit()]

## Instructions

Write a single JSON object mapping each node id to a one-sentence description
to: c:\Users\friveraq\Downloads\SisAlmacen 1 (1)\SisAlmacen\SisAlmacen\.graphify\description-instructions\batch-000.json

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
