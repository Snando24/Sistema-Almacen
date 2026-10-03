# Node Description Batch 4 of 11

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

- "db_bootstrap_build_alembic_config": "build_alembic_config()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/bootstrap.py:L32 | neighbors=[bootstrap.py, _resolve_runtime_path(), Construye la configuración de Alembic p…, run_migrations()] | lang=en
- "db_bootstrap_database_has_tables": "_database_has_tables()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/bootstrap.py:L47 | neighbors=[bootstrap.py, _bootstrap_sql_files(), Comprueba si la base ya contiene tablas…, run_migrations()] | lang=en
- "db_models_rationale_1": "Modelos SQLAlchemy base de SisAlmacen." | kind=entity | source=src/sisalmacen/infrastructure/db/models.py:L1 | neighbors=[Base, models.py, ScaledMoney, ScaledQuantity] | lang=nl
- "db_types": "types.py" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/types.py:L1 | neighbors=[ScaledDecimal, ScaledMoney, ScaledQuantity, TypeDecorators para cantidades y dinero…] | lang=en
- "domain_auth_dashboardrepository": "DashboardRepository" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L114 | neighbors=[auth.py, .get_snapshot(), Protocol, Puerto para métricas de la pantalla ini…] | lang=en
- "infrastructure_config": "config.py" | kind=code-symbol | source=src/sisalmacen/infrastructure/config.py:L1 | neighbors=[AppPaths, resolve_app_paths(), resolve_project_root(), Resolución de rutas y configuración bas…] | lang=en
- "infrastructure_config_resolve_app_paths": "resolve_app_paths()" | kind=code-symbol | source=src/sisalmacen/infrastructure/config.py:L25 | neighbors=[config.py, Construye las rutas persistentes princi…, AppPaths, resolve_project_root()] | lang=en
- "integration_test_auth_services_login_as_admin": "_login_as_admin()" | kind=code-symbol | source=tests/integration/test_auth_services.py:L415 | neighbors=[test_auth_services.py, test_user_management_creates_user_with_…, test_user_management_rejects_self_deact…, test_user_management_reset_password_for…] | lang=en
- "integration_test_auth_services_require_admin_id": "_require_admin_id()" | kind=code-symbol | source=tests/integration/test_auth_services.py:L410 | neighbors=[test_auth_services.py, test_change_password_rejects_incorrect_…, test_change_password_updates_hash_and_c…, test_user_management_rejects_deactivati…] | lang=en
- "integration_test_auth_services_test_change_password_rejects_incorrect_current_password": "test_change_password_rejects_incorrect_current_password()" | kind=code-symbol | source=tests/integration/test_auth_services.py:L158 | neighbors=[test_auth_services.py, _build_session_factory(), _require_admin_id(), _seed_admin()] | lang=en
- "integration_test_auth_services_test_user_management_creates_user_with_temporary_password": "test_user_management_creates_user_with_temporary_password()" | kind=code-symbol | source=tests/integration/test_auth_services.py:L199 | neighbors=[test_auth_services.py, _build_session_factory(), _login_as_admin(), _seed_admin()] | lang=en
- "integration_test_auth_services_test_user_management_rejects_missing_permission": "test_user_management_rejects_missing_permission()" | kind=code-symbol | source=tests/integration/test_auth_services.py:L240 | neighbors=[test_auth_services.py, _build_current_session(), _build_session_factory(), _seed_admin()] | lang=en
- "integration_test_auth_services_test_user_management_rejects_self_deactivation": "test_user_management_rejects_self_deactivation()" | kind=code-symbol | source=tests/integration/test_auth_services.py:L257 | neighbors=[test_auth_services.py, _build_session_factory(), _login_as_admin(), _seed_admin()] | lang=en
- "sisalmacen_bootstrap": "bootstrap.py" | kind=code-symbol | source=src/sisalmacen/bootstrap.py:L1 | neighbors=[AppContext, bootstrap_application(), Bootstrap principal de la aplicación., main.py] | lang=en
- "sisalmacen_bootstrap_appcontext": "AppContext" | kind=code-symbol | source=src/sisalmacen/bootstrap.py:L17 | neighbors=[bootstrap.py, AppPaths, bootstrap_application(), Dependencias principales de ejecución.] | lang=en
- "ui_main_window_mainwindow_build_content": "._build_content()" | kind=code-symbol | source=src/sisalmacen/ui/main_window.py:L156 | neighbors=[MainWindow, ._build_dashboard_page(), ._build_section_page(), ._setup_ui()] | lang=en
- "ui_main_window_mainwindow_build_dashboard_page": "._build_dashboard_page()" | kind=code-symbol | source=src/sisalmacen/ui/main_window.py:L267 | neighbors=[MainWindow, ._build_content(), ._build_info_panels(), ._build_stats_grid()] | lang=en
- "ui_main_window_mainwindow_render_stats": "._render_stats()" | kind=code-symbol | source=src/sisalmacen/ui/main_window.py:L429 | neighbors=[MainWindow, ._build_stats_grid(), ._refresh_snapshot(), ._build_stat_card()] | lang=en
- "ui_test_main_window_navigation": "test_main_window_navigation.py" | kind=code-symbol | source=tests/ui/test_main_window_navigation.py:L1 | neighbors=[_build_session(), _build_snapshot(), test_main_window_switches_between_secti…, Pruebas de navegación principal de la a…] | lang=en
- "application_auth_changepasswordservice_change_password": ".change_password()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L289 | neighbors=[ChangePasswordService, .verify(), Actualiza la contraseña del usuario y l…] | lang=en
- "application_auth_initialsetupservice_create_initial_admin": ".create_initial_admin()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L115 | neighbors=[InitialSetupService, .requires_initial_setup(), Crea el primer usuario ADMIN y la confi…] | lang=en
- "application_auth_initialsetupservice_requires_initial_setup": ".requires_initial_setup()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L110 | neighbors=[InitialSetupService, .create_initial_admin(), Indica si aún no existe ningún usuario.] | lang=en
- "application_auth_passwordhasherport_verify": ".verify()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L91 | neighbors=[.authenticate(), .change_password(), PasswordHasherPort] | lang=en
- "application_auth_usermanagementservice_ensure_username_available": "._ensure_username_available()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L499 | neighbors=[UserManagementService, .create_user(), .update_user()] | lang=en
- "application_auth_usermanagementservice_list_roles": ".list_roles()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L375 | neighbors=[Lista roles disponibles para la UI admi…, UserManagementService, .require_permission()] | lang=en
- "application_auth_usermanagementservice_list_users": ".list_users()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L381 | neighbors=[Devuelve usuarios registrados ordenados…, UserManagementService, .require_permission()] | lang=en
- "application_auth_usermanagementservice_require_role": "._require_role()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L490 | neighbors=[UserManagementService, .create_user(), .update_user()] | lang=en
- "application_auth_usermanagementservice_require_user": "._require_user()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L481 | neighbors=[UserManagementService, .reset_password(), .update_user()] | lang=en
- "application_auth_usermanagementservice_validate_password_policy": "._validate_password_policy()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L515 | neighbors=[UserManagementService, .create_user(), .reset_password()] | lang=en
- "application_uow": "uow.py" | kind=code-symbol | source=src/sisalmacen/application/uow.py:L1 | neighbors=[ABC, UnitOfWork, Contrato de unidad de trabajo para caso…] | lang=en
- "application_uow_unitofwork_rollback": ".rollback()" | kind=code-symbol | source=src/sisalmacen/application/uow.py:L24 | neighbors=[Revierte la transacción activa., UnitOfWork, .__exit__()] | lang=en
- "db_001_schema_inventario": "inventario" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L136 | neighbors=[001_schema.sql, producto, trg_producto_inventario] | lang=en
- "db_001_schema_rol": "rol" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L17 | neighbors=[001_schema.sql, rol_permiso, usuario] | lang=en
- "db_001_schema_rol_permiso": "rol_permiso" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L31 | neighbors=[001_schema.sql, permiso, rol] | lang=en
- "db_001_schema_trg_producto_inventario": "trg_producto_inventario" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L254 | neighbors=[001_schema.sql, inventario, producto] | lang=en
- "db_auth_repositories_map_auth_user": "_map_auth_user()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L202 | neighbors=[auth_repositories.py, .get_by_id(), .get_by_username()] | lang=en
- "db_auth_repositories_sqlalchemyuserrepository_add": ".add()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L68 | neighbors=[.set_many(), SqlAlchemyUserRepository, .get_role_by_code()] | lang=en
- "db_repositories_rationale_1": "Repositorios base sobre SQLAlchemy." | kind=entity | source=src/sisalmacen/infrastructure/db/repositories.py:L1 | neighbors=[Base, repositories.py, Repository] | lang=en
- "db_repositories_rationale_17": "Implementación mínima de repositorio para la Entrega 0." | kind=entity | source=src/sisalmacen/infrastructure/db/repositories.py:L17 | neighbors=[Base, SqlAlchemyRepository, Repository] | lang=es
- "db_session": "session.py" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/session.py:L1 | neighbors=[create_session_factory(), create_sqlite_engine(), Creación de engine y sesiones SQLite.] | lang=en

## Instructions

Write a single JSON object mapping each node id to a one-sentence description
to: c:\Users\friveraq\Downloads\SisAlmacen 1 (1)\SisAlmacen\SisAlmacen\.graphify\description-instructions\batch-003.json

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
