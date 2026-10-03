# Node Description Batch 6 of 11

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

- "db_001_schema_trg_auditoria_no_delete": "trg_auditoria_no_delete" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L235 | neighbors=[001_schema.sql, auditoria]
- "db_001_schema_trg_auditoria_no_update": "trg_auditoria_no_update" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L233 | neighbors=[001_schema.sql, auditoria]
- "db_001_schema_trg_detmov_no_delete": "trg_detmov_no_delete" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L245 | neighbors=[001_schema.sql, detalle_movimiento]
- "db_001_schema_trg_detmov_no_update": "trg_detmov_no_update" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L243 | neighbors=[001_schema.sql, detalle_movimiento]
- "db_001_schema_trg_detmov_producto_activo": "trg_detmov_producto_activo" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L249 | neighbors=[001_schema.sql, detalle_movimiento]
- "db_001_schema_trg_movimiento_no_delete": "trg_movimiento_no_delete" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L240 | neighbors=[001_schema.sql, movimiento]
- "db_001_schema_trg_movimiento_no_update": "trg_movimiento_no_update" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L238 | neighbors=[001_schema.sql, movimiento]
- "db_001_schema_unidad_medida": "unidad_medida" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L69 | neighbors=[001_schema.sql, producto]
- "db_auth_repositories_count": "_count()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L234 | neighbors=[auth_repositories.py, .get_snapshot()]
- "db_auth_repositories_map_user_summary": "_map_user_summary()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L219 | neighbors=[auth_repositories.py, .list_users()]
- "db_auth_repositories_sqlalchemyconfigurationrepository_set_many": ".set_many()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L169 | neighbors=[SqlAlchemyConfigurationRepository, .add()]
- "db_auth_repositories_sqlalchemydashboardrepository_get_snapshot": ".get_snapshot()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L185 | neighbors=[SqlAlchemyDashboardRepository, _count()]
- "db_auth_repositories_sqlalchemyuserrepository_count_active_admins": ".count_active_admins()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L135 | neighbors=[SqlAlchemyUserRepository, ._scalar()]
- "db_auth_repositories_sqlalchemyuserrepository_count_active_users": ".count_active_users()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L41 | neighbors=[SqlAlchemyUserRepository, ._scalar()]
- "db_auth_repositories_sqlalchemyuserrepository_count_users": ".count_users()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L38 | neighbors=[SqlAlchemyUserRepository, ._scalar()]
- "db_auth_repositories_sqlalchemyuserrepository_get_by_id": ".get_by_id()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L44 | neighbors=[SqlAlchemyUserRepository, _map_auth_user()]
- "db_auth_repositories_sqlalchemyuserrepository_get_by_username": ".get_by_username()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L56 | neighbors=[SqlAlchemyUserRepository, _map_auth_user()]
- "db_auth_repositories_sqlalchemyuserrepository_get_role_by_code": ".get_role_by_code()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L115 | neighbors=[SqlAlchemyUserRepository, .add()]
- "db_auth_repositories_sqlalchemyuserrepository_list_users": ".list_users()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L130 | neighbors=[SqlAlchemyUserRepository, _map_user_summary()]
- "db_base": "base.py" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/base.py:L1 | neighbors=[Base, Base declarativa y metadatos SQLAlchemy.]
- "db_repositories": "repositories.py" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/repositories.py:L1 | neighbors=[SqlAlchemyRepository, Repositorios base sobre SQLAlchemy.]
- "db_session_create_session_factory": "create_session_factory()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/session.py:L35 | neighbors=[session.py, Construye la factoría de sesiones usada…]
- "db_session_create_sqlite_engine": "create_sqlite_engine()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/session.py:L12 | neighbors=[session.py, Crea un engine SQLite con las pragmas o…]
- "db_uow": "uow.py" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/uow.py:L1 | neighbors=[SqlAlchemyUnitOfWork, Unidad de trabajo basada en SQLAlchemy.]
- "db_uow_rationale_1": "Unidad de trabajo basada en SQLAlchemy." | kind=entity | source=src/sisalmacen/infrastructure/db/uow.py:L1 | neighbors=[UnitOfWork, uow.py]
- "db_uow_rationale_11": "Implementación concreta de la unidad de trabajo." | kind=entity | source=src/sisalmacen/infrastructure/db/uow.py:L11 | neighbors=[UnitOfWork, SqlAlchemyUnitOfWork]
- "db_uow_sqlalchemyunitofwork_exit": ".__exit__()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/uow.py:L21 | neighbors=[SqlAlchemyUnitOfWork, .rollback()]
- "db_uow_sqlalchemyunitofwork_rollback": ".rollback()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/uow.py:L35 | neighbors=[SqlAlchemyUnitOfWork, .__exit__()]
- "dialogs_initial_setup_dialog": "initial_setup_dialog.py" | kind=code-symbol | source=src/sisalmacen/ui/dialogs/initial_setup_dialog.py:L1 | neighbors=[InitialSetupDialog, Asistente de primer arranque.]
- "dialogs_initial_setup_dialog_initialsetupdialog_init": ".__init__()" | kind=code-symbol | source=src/sisalmacen/ui/dialogs/initial_setup_dialog.py:L29 | neighbors=[InitialSetupDialog, ._setup_ui()]
- "dialogs_initial_setup_dialog_initialsetupdialog_setup_ui": "._setup_ui()" | kind=code-symbol | source=src/sisalmacen/ui/dialogs/initial_setup_dialog.py:L42 | neighbors=[InitialSetupDialog, .__init__()]
- "dialogs_initial_setup_dialog_initialsetupdialog_suggested_username": ".suggested_username()" | kind=code-symbol | source=src/sisalmacen/ui/dialogs/initial_setup_dialog.py:L123 | neighbors=[InitialSetupDialog, Devuelve el usuario ingresado, útil par…]
- "dialogs_login_dialog": "login_dialog.py" | kind=code-symbol | source=src/sisalmacen/ui/dialogs/login_dialog.py:L1 | neighbors=[LoginDialog, Diálogo de autenticación local.]
- "dialogs_login_dialog_logindialog_init": ".__init__()" | kind=code-symbol | source=src/sisalmacen/ui/dialogs/login_dialog.py:L28 | neighbors=[LoginDialog, ._setup_ui()]
- "dialogs_login_dialog_logindialog_session": ".session()" | kind=code-symbol | source=src/sisalmacen/ui/dialogs/login_dialog.py:L45 | neighbors=[LoginDialog, Sesión autenticada resultante del diálo…]
- "dialogs_login_dialog_logindialog_setup_ui": "._setup_ui()" | kind=code-symbol | source=src/sisalmacen/ui/dialogs/login_dialog.py:L50 | neighbors=[LoginDialog, .__init__()]
- "domain_auth_authuser": "AuthUser" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L11 | neighbors=[auth.py, Representa un usuario autenticable del …]
- "domain_auth_configurationrepository_get_many": ".get_many()" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L107 | neighbors=[ConfigurationRepository, Obtiene varias claves de configuración.]
- "domain_auth_configurationrepository_set_many": ".set_many()" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L110 | neighbors=[ConfigurationRepository, Actualiza varias claves de configuració…]
- "domain_auth_dashboardrepository_get_snapshot": ".get_snapshot()" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L117 | neighbors=[DashboardRepository, Construye el resumen inicial mostrado e…]

## Instructions

Write a single JSON object mapping each node id to a one-sentence description
to: c:\Users\friveraq\Downloads\SisAlmacen 1 (1)\SisAlmacen\SisAlmacen\.graphify\description-instructions\batch-005.json

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
