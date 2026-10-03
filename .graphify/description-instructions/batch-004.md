# Node Description Batch 5 of 11

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

- "dialogs_initial_setup_dialog_rationale_1": "Asistente de primer arranque." | kind=entity | source=src/sisalmacen/ui/dialogs/initial_setup_dialog.py:L1 | neighbors=[InitialAdminPayload, initial_setup_dialog.py, DomainError] | lang=nl
- "dialogs_initial_setup_dialog_rationale_124": "Devuelve el usuario ingresado, útil para prefijar el login." | kind=entity | source=src/sisalmacen/ui/dialogs/initial_setup_dialog.py:L124 | neighbors=[InitialAdminPayload, .suggested_username(), DomainError] | lang=es
- "dialogs_initial_setup_dialog_rationale_27": "Solicita los datos básicos del primer administrador." | kind=entity | source=src/sisalmacen/ui/dialogs/initial_setup_dialog.py:L27 | neighbors=[InitialAdminPayload, InitialSetupDialog, DomainError] | lang=es
- "dialogs_login_dialog_rationale_1": "Diálogo de autenticación local." | kind=entity | source=src/sisalmacen/ui/dialogs/login_dialog.py:L1 | neighbors=[CurrentSession, login_dialog.py, DomainError] | lang=nl
- "dialogs_login_dialog_rationale_26": "Solicita credenciales para ingresar al sistema." | kind=entity | source=src/sisalmacen/ui/dialogs/login_dialog.py:L26 | neighbors=[CurrentSession, LoginDialog, DomainError] | lang=en
- "dialogs_login_dialog_rationale_46": "Sesión autenticada resultante del diálogo." | kind=entity | source=src/sisalmacen/ui/dialogs/login_dialog.py:L46 | neighbors=[CurrentSession, .session(), DomainError] | lang=en
- "infrastructure_config_resolve_project_root": "resolve_project_root()" | kind=code-symbol | source=src/sisalmacen/infrastructure/config.py:L19 | neighbors=[config.py, Obtiene la raíz del proyecto en modo de…, resolve_app_paths()] | lang=en
- "integration_test_auth_services_test_authentication_accepts_valid_credentials": "test_authentication_accepts_valid_credentials()" | kind=code-symbol | source=tests/integration/test_auth_services.py:L78 | neighbors=[test_auth_services.py, _build_session_factory(), _seed_admin()] | lang=en
- "integration_test_auth_services_test_authentication_rejects_invalid_password": "test_authentication_rejects_invalid_password()" | kind=code-symbol | source=tests/integration/test_auth_services.py:L99 | neighbors=[test_auth_services.py, _build_session_factory(), _seed_admin()] | lang=en
- "integration_test_schema_reference_test_initial_migration_matches_reference_schema": "test_initial_migration_matches_reference_schema()" | kind=code-symbol | source=tests/integration/test_schema_reference.py:L33 | neighbors=[test_schema_reference.py, _execute_script(), _schema_snapshot()] | lang=en
- "integration_test_uow": "test_uow.py" | kind=code-symbol | source=tests/integration/test_uow.py:L1 | neighbors=[test_sqlalchemy_uow_commit_persists_cha…, test_sqlalchemy_uow_rollback_discards_c…, Pruebas mínimas de la unidad de trabajo.] | lang=en
- "migrations_env": "env.py" | kind=code-symbol | source=src/sisalmacen/infrastructure/migrations/env.py:L1 | neighbors=[run_migrations_offline(), run_migrations_online(), Entorno Alembic para SisAlmacen.] | lang=en
- "protocol": "Protocol" | kind=code-symbol | neighbors=[ConfigurationRepository, DashboardRepository, UserRepository] | lang=en
- "sisalmacen_bootstrap_bootstrap_application": "bootstrap_application()" | kind=code-symbol | source=src/sisalmacen/bootstrap.py:L25 | neighbors=[bootstrap.py, AppContext, Prepara rutas, logging, migraciones y c…] | lang=en
- "ui_main_window_mainwindow_build_info_panels": "._build_info_panels()" | kind=code-symbol | source=src/sisalmacen/ui/main_window.py:L377 | neighbors=[MainWindow, ._build_dashboard_page(), ._build_info_row()] | lang=en
- "ui_main_window_mainwindow_build_section_page": "._build_section_page()" | kind=code-symbol | source=src/sisalmacen/ui/main_window.py:L319 | neighbors=[MainWindow, ._build_content(), ._build_stat_card()] | lang=en
- "ui_main_window_mainwindow_build_stat_card": "._build_stat_card()" | kind=code-symbol | source=src/sisalmacen/ui/main_window.py:L462 | neighbors=[MainWindow, ._build_section_page(), ._render_stats()] | lang=en
- "ui_main_window_mainwindow_build_stats_grid": "._build_stats_grid()" | kind=code-symbol | source=src/sisalmacen/ui/main_window.py:L311 | neighbors=[MainWindow, ._build_dashboard_page(), ._render_stats()] | lang=en
- "ui_test_main_window_navigation_rationale_1": "Pruebas de navegación principal de la aplicación." | kind=entity | source=tests/ui/test_main_window_navigation.py:L1 | neighbors=[CurrentSession, MainWindow, test_main_window_navigation.py] | lang=nl
- "ui_test_main_window_navigation_test_main_window_switches_between_sections": "test_main_window_switches_between_sections()" | kind=code-symbol | source=tests/ui/test_main_window_navigation.py:L37 | neighbors=[test_main_window_navigation.py, _build_session(), _build_snapshot()] | lang=en
- "unit_test_brand_theme": "test_brand_theme.py" | kind=code-symbol | source=tests/unit/test_brand_theme.py:L1 | neighbors=[test_brand_palette_has_company_colors(), test_brand_stylesheet_contains_expected…, Pruebas del branding corporativo de la …] | lang=en
- "unit_test_types_rationale_1": "Pruebas de TypeDecorator para decimales escalados." | kind=entity | source=tests/unit/test_types.py:L1 | neighbors=[ScaledMoney, ScaledQuantity, test_types.py] | lang=en
- "versions_0001_initial_run_script": "_run_script()" | kind=code-symbol | source=src/sisalmacen/infrastructure/migrations/versions/0001_initial.py:L33 | neighbors=[0001_initial.py, _sqlite_connection(), upgrade()] | lang=en
- "versions_0001_initial_upgrade": "upgrade()" | kind=code-symbol | source=src/sisalmacen/infrastructure/migrations/versions/0001_initial.py:L39 | neighbors=[0001_initial.py, _repo_root(), _run_script()] | lang=en
- "abc": "ABC" | kind=code-symbol | neighbors=[uow.py, UnitOfWork] | lang=en
- "application_auth_dashboardservice_get_snapshot": ".get_snapshot()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L563 | neighbors=[DashboardService, Devuelve el estado agregado del sistema…] | lang=en
- "application_auth_format_utc": "_format_utc()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L573 | neighbors=[auth.py, .authenticate()] | lang=en
- "application_auth_parse_utc": "_parse_utc()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L577 | neighbors=[auth.py, .authenticate()] | lang=en
- "application_auth_require_user_id": "_require_user_id()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L583 | neighbors=[auth.py, .authenticate()] | lang=en
- "application_auth_usermanagementservice_init": ".__init__()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L363 | neighbors=[UserManagementService, AuthorizationService] | lang=en
- "application_auth_usermanagementservice_validate_user_state_transition": "._validate_user_state_transition()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L528 | neighbors=[UserManagementService, .update_user()] | lang=en
- "application_auth_utc_now": "_utc_now()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L569 | neighbors=[auth.py, .authenticate()] | lang=en
- "application_uow_unitofwork_commit": ".commit()" | kind=code-symbol | source=src/sisalmacen/application/uow.py:L20 | neighbors=[Confirma la transacción activa., UnitOfWork] | lang=en
- "application_uow_unitofwork_exit": ".__exit__()" | kind=code-symbol | source=src/sisalmacen/application/uow.py:L14 | neighbors=[UnitOfWork, .rollback()] | lang=en
- "db_001_schema_categoria": "categoria" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L54 | neighbors=[001_schema.sql, producto] | lang=en
- "db_001_schema_detalle_importacion": "detalle_importacion" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L174 | neighbors=[001_schema.sql, importacion] | lang=en
- "db_001_schema_marca": "marca" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L62 | neighbors=[001_schema.sql, producto] | lang=en
- "db_001_schema_permiso": "permiso" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L25 | neighbors=[001_schema.sql, rol_permiso] | lang=en
- "db_001_schema_proveedor": "proveedor" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L78 | neighbors=[001_schema.sql, producto] | lang=en
- "db_001_schema_tipo_movimiento": "tipo_movimiento" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L144 | neighbors=[001_schema.sql, movimiento] | lang=en

## Instructions

Write a single JSON object mapping each node id to a one-sentence description
to: c:\Users\friveraq\Downloads\SisAlmacen 1 (1)\SisAlmacen\SisAlmacen\.graphify\description-instructions\batch-004.json

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
