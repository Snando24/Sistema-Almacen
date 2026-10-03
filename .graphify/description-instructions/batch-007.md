# Node Description Batch 8 of 11

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

- "sisalmacen_main_requires_initial_setup": "_requires_initial_setup()" | kind=code-symbol | source=src/sisalmacen/main.py:L89 | neighbors=[main.py, main()]
- "tests_conftest": "conftest.py" | kind=code-symbol | source=tests/conftest.py:L1 | neighbors=[project_root(), Fixtures compartidas de pruebas.]
- "ui_main_window": "main_window.py" | kind=code-symbol | source=src/sisalmacen/ui/main_window.py:L1 | neighbors=[MainWindow, Ventana principal de la aplicación loca…]
- "ui_main_window_mainwindow_build_info_row": "._build_info_row()" | kind=code-symbol | source=src/sisalmacen/ui/main_window.py:L415 | neighbors=[MainWindow, ._build_info_panels()]
- "ui_main_window_mainwindow_build_menu": "._build_menu()" | kind=code-symbol | source=src/sisalmacen/ui/main_window.py:L146 | neighbors=[MainWindow, ._setup_ui()]
- "ui_main_window_mainwindow_build_sidebar": "._build_sidebar()" | kind=code-symbol | source=src/sisalmacen/ui/main_window.py:L82 | neighbors=[MainWindow, ._setup_ui()]
- "ui_main_window_mainwindow_init": ".__init__()" | kind=code-symbol | source=src/sisalmacen/ui/main_window.py:L34 | neighbors=[MainWindow, ._setup_ui()]
- "ui_main_window_mainwindow_refresh_snapshot": "._refresh_snapshot()" | kind=code-symbol | source=src/sisalmacen/ui/main_window.py:L483 | neighbors=[MainWindow, ._render_stats()]
- "ui_main_window_rationale_1": "Ventana principal de la aplicación local." | kind=entity | source=src/sisalmacen/ui/main_window.py:L1 | neighbors=[CurrentSession, main_window.py]
- "ui_main_window_rationale_32": "Ventana principal inicial lista para operación local." | kind=entity | source=src/sisalmacen/ui/main_window.py:L32 | neighbors=[CurrentSession, MainWindow]
- "ui_test_main_window_navigation_build_session": "_build_session()" | kind=code-symbol | source=tests/ui/test_main_window_navigation.py:L12 | neighbors=[test_main_window_navigation.py, test_main_window_switches_between_secti…]
- "ui_test_main_window_navigation_build_snapshot": "_build_snapshot()" | kind=code-symbol | source=tests/ui/test_main_window_navigation.py:L24 | neighbors=[test_main_window_navigation.py, test_main_window_switches_between_secti…]
- "ui_theme": "theme.py" | kind=code-symbol | source=src/sisalmacen/ui/theme.py:L1 | neighbors=[get_brand_style_sheet(), Tema visual corporativo para la aplicac…]
- "ui_theme_get_brand_style_sheet": "get_brand_style_sheet()" | kind=code-symbol | source=src/sisalmacen/ui/theme.py:L20 | neighbors=[theme.py, Devuelve la hoja de estilo con identida…]
- "unit_test_types": "test_types.py" | kind=code-symbol | source=tests/unit/test_types.py:L1 | neighbors=[test_scaled_decimal_round_trip_preserve…, Pruebas de TypeDecorator para decimales…]
- "versions_0001_initial_repo_root": "_repo_root()" | kind=code-symbol | source=src/sisalmacen/infrastructure/migrations/versions/0001_initial.py:L17 | neighbors=[0001_initial.py, upgrade()]
- "versions_0001_initial_sqlite_connection": "_sqlite_connection()" | kind=code-symbol | source=src/sisalmacen/infrastructure/migrations/versions/0001_initial.py:L21 | neighbors=[0001_initial.py, _run_script()]
- "application_auth_authenticationservice_init": ".__init__()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L200 | neighbors=[AuthenticationService]
- "application_auth_changepasswordservice_get_password_min_length": "._get_password_min_length()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L338 | neighbors=[ChangePasswordService]
- "application_auth_changepasswordservice_init": ".__init__()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L279 | neighbors=[ChangePasswordService]
- "application_auth_dashboardservice_init": ".__init__()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L560 | neighbors=[DashboardService]
- "application_auth_initialsetupservice_get_password_min_length": "._get_password_min_length()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L189 | neighbors=[InitialSetupService]
- "application_auth_initialsetupservice_init": ".__init__()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L100 | neighbors=[InitialSetupService]
- "application_auth_passwordhasherport_hash": ".hash()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L88 | neighbors=[PasswordHasherPort]
- "application_auth_usermanagementservice_get_password_min_length": "._get_password_min_length()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L551 | neighbors=[UserManagementService]
- "application_init": "__init__.py" | kind=code-symbol | source=src/sisalmacen/application/__init__.py:L1 | neighbors=[Capa de aplicación de SisAlmacen.]
- "application_init_rationale_1": "Capa de aplicación de SisAlmacen." | kind=entity | source=src/sisalmacen/application/__init__.py:L1 | neighbors=[__init__.py]
- "application_uow_rationale_1": "Contrato de unidad de trabajo para casos de uso." | kind=entity | source=src/sisalmacen/application/uow.py:L1 | neighbors=[uow.py]
- "application_uow_rationale_21": "Confirma la transacción activa." | kind=entity | source=src/sisalmacen/application/uow.py:L21 | neighbors=[.commit()]
- "application_uow_rationale_25": "Revierte la transacción activa." | kind=entity | source=src/sisalmacen/application/uow.py:L25 | neighbors=[.rollback()]
- "application_uow_rationale_9": "Unidad de trabajo abstracta para coordinar transacciones." | kind=entity | source=src/sisalmacen/application/uow.py:L9 | neighbors=[UnitOfWork]
- "application_uow_unitofwork_enter": ".__enter__()" | kind=code-symbol | source=src/sisalmacen/application/uow.py:L11 | neighbors=[UnitOfWork]
- "configurationrepository": "ConfigurationRepository" | kind=code-symbol | neighbors=[SqlAlchemyConfigurationRepository]
- "dashboardrepository": "DashboardRepository" | kind=code-symbol | neighbors=[SqlAlchemyDashboardRepository]
- "db_001_schema_configuracion": "configuracion" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L9 | neighbors=[001_schema.sql]
- "db_auth_repositories_sqlalchemyconfigurationrepository_get_many": ".get_many()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L162 | neighbors=[SqlAlchemyConfigurationRepository]
- "db_auth_repositories_sqlalchemyconfigurationrepository_init": ".__init__()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L159 | neighbors=[SqlAlchemyConfigurationRepository]
- "db_auth_repositories_sqlalchemydashboardrepository_init": ".__init__()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L182 | neighbors=[SqlAlchemyDashboardRepository]
- "db_auth_repositories_sqlalchemyuserrepository_init": ".__init__()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L35 | neighbors=[SqlAlchemyUserRepository]
- "db_auth_repositories_sqlalchemyuserrepository_list_permission_codes": ".list_permission_codes()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L143 | neighbors=[SqlAlchemyUserRepository]

## Instructions

Write a single JSON object mapping each node id to a one-sentence description
to: c:\Users\friveraq\Downloads\SisAlmacen 1 (1)\SisAlmacen\SisAlmacen\.graphify\description-instructions\batch-007.json

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
