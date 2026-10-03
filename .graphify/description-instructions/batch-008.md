# Node Description Batch 9 of 11

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

- "db_auth_repositories_sqlalchemyuserrepository_list_roles": ".list_roles()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L123 | neighbors=[SqlAlchemyUserRepository] | lang=en
- "db_auth_repositories_sqlalchemyuserrepository_save": ".save()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L100 | neighbors=[SqlAlchemyUserRepository] | lang=en
- "db_base_rationale_1": "Base declarativa y metadatos SQLAlchemy." | kind=entity | source=src/sisalmacen/infrastructure/db/base.py:L1 | neighbors=[base.py] | lang=es
- "db_base_rationale_18": "Base declarativa común para los modelos." | kind=entity | source=src/sisalmacen/infrastructure/db/base.py:L18 | neighbors=[Base] | lang=en
- "db_bootstrap_rationale_1": "Inicialización de la base de datos y migraciones." | kind=entity | source=src/sisalmacen/infrastructure/db/bootstrap.py:L1 | neighbors=[bootstrap.py] | lang=en
- "db_bootstrap_rationale_14": "Resuelve la ruta real de archivos de recursos tanto en desarrollo como empaqueta" | kind=entity | source=src/sisalmacen/infrastructure/db/bootstrap.py:L14 | neighbors=[_resolve_runtime_path()] | lang=en
- "db_bootstrap_rationale_33": "Construye la configuración de Alembic para una base destino." | kind=entity | source=src/sisalmacen/infrastructure/db/bootstrap.py:L33 | neighbors=[build_alembic_config()] | lang=es
- "db_bootstrap_rationale_48": "Comprueba si la base ya contiene tablas creadas." | kind=entity | source=src/sisalmacen/infrastructure/db/bootstrap.py:L48 | neighbors=[_database_has_tables()] | lang=en
- "db_bootstrap_rationale_61": "Crea la Base de Datos desde los SQL de referencia cuando no hay migración dispon" | kind=entity | source=src/sisalmacen/infrastructure/db/bootstrap.py:L61 | neighbors=[_bootstrap_sql_files()] | lang=en
- "db_bootstrap_rationale_81": "Aplica todas las migraciones pendientes a la base indicada." | kind=entity | source=src/sisalmacen/infrastructure/db/bootstrap.py:L81 | neighbors=[run_migrations()] | lang=es
- "db_init": "__init__.py" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/__init__.py:L1 | neighbors=[Infraestructura de base de datos.] | lang=en
- "db_init_rationale_1": "Infraestructura de base de datos." | kind=entity | source=src/sisalmacen/infrastructure/db/__init__.py:L1 | neighbors=[__init__.py] | lang=nl
- "db_repositories_sqlalchemyrepository_add": ".add()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/repositories.py:L23 | neighbors=[SqlAlchemyRepository] | lang=en
- "db_repositories_sqlalchemyrepository_get_by_id": ".get_by_id()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/repositories.py:L26 | neighbors=[SqlAlchemyRepository] | lang=en
- "db_repositories_sqlalchemyrepository_init": ".__init__()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/repositories.py:L19 | neighbors=[SqlAlchemyRepository] | lang=en
- "db_session_rationale_1": "Creación de engine y sesiones SQLite." | kind=entity | source=src/sisalmacen/infrastructure/db/session.py:L1 | neighbors=[session.py] | lang=en
- "db_session_rationale_13": "Crea un engine SQLite con las pragmas obligatorias." | kind=entity | source=src/sisalmacen/infrastructure/db/session.py:L13 | neighbors=[create_sqlite_engine()] | lang=es
- "db_session_rationale_36": "Construye la factoría de sesiones usada por la aplicación." | kind=entity | source=src/sisalmacen/infrastructure/db/session.py:L36 | neighbors=[create_session_factory()] | lang=es
- "db_types_rationale_1": "TypeDecorators para cantidades y dinero escalados." | kind=entity | source=src/sisalmacen/infrastructure/db/types.py:L1 | neighbors=[types.py] | lang=es
- "db_types_rationale_12": "Persiste decimales como enteros escalados." | kind=entity | source=src/sisalmacen/infrastructure/db/types.py:L12 | neighbors=[ScaledDecimal] | lang=en
- "db_types_rationale_36": "Cantidad con precisión de 3 decimales." | kind=entity | source=src/sisalmacen/infrastructure/db/types.py:L36 | neighbors=[ScaledQuantity] | lang=en
- "db_types_rationale_45": "Dinero con precisión de 4 decimales." | kind=entity | source=src/sisalmacen/infrastructure/db/types.py:L45 | neighbors=[ScaledMoney] | lang=en
- "db_types_scaleddecimal_init": ".__init__()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/types.py:L17 | neighbors=[ScaledDecimal] | lang=en
- "db_types_scaleddecimal_process_bind_param": ".process_bind_param()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/types.py:L23 | neighbors=[ScaledDecimal] | lang=en
- "db_types_scaleddecimal_process_result_value": ".process_result_value()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/types.py:L29 | neighbors=[ScaledDecimal] | lang=en
- "db_types_scaledmoney_init": ".__init__()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/types.py:L49 | neighbors=[ScaledMoney] | lang=en
- "db_types_scaledquantity_init": ".__init__()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/types.py:L40 | neighbors=[ScaledQuantity] | lang=en
- "db_uow_sqlalchemyunitofwork_commit": ".commit()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/uow.py:L30 | neighbors=[SqlAlchemyUnitOfWork] | lang=en
- "db_uow_sqlalchemyunitofwork_enter": ".__enter__()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/uow.py:L17 | neighbors=[SqlAlchemyUnitOfWork] | lang=en
- "db_uow_sqlalchemyunitofwork_init": ".__init__()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/uow.py:L13 | neighbors=[SqlAlchemyUnitOfWork] | lang=en
- "declarativebase": "DeclarativeBase" | kind=code-symbol | neighbors=[Base] | lang=en
- "dialogs_init": "__init__.py" | kind=code-symbol | source=src/sisalmacen/ui/dialogs/__init__.py:L1 | neighbors=[Diálogos de la interfaz principal.] | lang=en
- "dialogs_init_rationale_1": "Diálogos de la interfaz principal." | kind=entity | source=src/sisalmacen/ui/dialogs/__init__.py:L1 | neighbors=[__init__.py] | lang=en
- "dialogs_initial_setup_dialog_initialsetupdialog_submit": "._submit()" | kind=code-symbol | source=src/sisalmacen/ui/dialogs/initial_setup_dialog.py:L128 | neighbors=[InitialSetupDialog] | lang=en
- "dialogs_login_dialog_logindialog_submit": "._submit()" | kind=code-symbol | source=src/sisalmacen/ui/dialogs/login_dialog.py:L114 | neighbors=[LoginDialog] | lang=en
- "domain_auth_rationale_1": "Modelos y puertos para autenticación y estado inicial." | kind=entity | source=src/sisalmacen/domain/auth.py:L1 | neighbors=[auth.py] | lang=es
- "domain_auth_rationale_101": "Lista permisos asignados a un rol." | kind=entity | source=src/sisalmacen/domain/auth.py:L101 | neighbors=[.list_permission_codes()] | lang=en
- "domain_auth_rationale_105": "Puerto para configuración persistente." | kind=entity | source=src/sisalmacen/domain/auth.py:L105 | neighbors=[ConfigurationRepository] | lang=en
- "domain_auth_rationale_108": "Obtiene varias claves de configuración." | kind=entity | source=src/sisalmacen/domain/auth.py:L108 | neighbors=[.get_many()] | lang=nl
- "domain_auth_rationale_111": "Actualiza varias claves de configuración." | kind=entity | source=src/sisalmacen/domain/auth.py:L111 | neighbors=[.set_many()] | lang=nl

## Instructions

Write a single JSON object mapping each node id to a one-sentence description
to: c:\Users\friveraq\Downloads\SisAlmacen 1 (1)\SisAlmacen\SisAlmacen\.graphify\description-instructions\batch-008.json

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
