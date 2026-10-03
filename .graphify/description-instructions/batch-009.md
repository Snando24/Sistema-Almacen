# Node Description Batch 10 of 11

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

- "domain_auth_rationale_115": "Puerto para métricas de la pantalla inicial." | kind=entity | source=src/sisalmacen/domain/auth.py:L115 | neighbors=[DashboardRepository] | lang=en
- "domain_auth_rationale_118": "Construye el resumen inicial mostrado en la UI." | kind=entity | source=src/sisalmacen/domain/auth.py:L118 | neighbors=[.get_snapshot()] | lang=es
- "domain_auth_rationale_12": "Representa un usuario autenticable del sistema." | kind=entity | source=src/sisalmacen/domain/auth.py:L12 | neighbors=[AuthUser] | lang=en
- "domain_auth_rationale_30": "Rol disponible en el sistema." | kind=entity | source=src/sisalmacen/domain/auth.py:L30 | neighbors=[RoleInfo] | lang=es
- "domain_auth_rationale_39": "Resumen de usuario para administración." | kind=entity | source=src/sisalmacen/domain/auth.py:L39 | neighbors=[UserSummary] | lang=en
- "domain_auth_rationale_55": "Resumen para la pantalla inicial local." | kind=entity | source=src/sisalmacen/domain/auth.py:L55 | neighbors=[DashboardSnapshot] | lang=es
- "domain_auth_rationale_68": "Puerto de lectura y escritura de usuarios." | kind=entity | source=src/sisalmacen/domain/auth.py:L68 | neighbors=[UserRepository] | lang=nl
- "domain_auth_rationale_71": "Devuelve el total de usuarios." | kind=entity | source=src/sisalmacen/domain/auth.py:L71 | neighbors=[.count_users()] | lang=en
- "domain_auth_rationale_74": "Devuelve el total de usuarios activos." | kind=entity | source=src/sisalmacen/domain/auth.py:L74 | neighbors=[.count_active_users()] | lang=en
- "domain_auth_rationale_77": "Busca un usuario por identificador." | kind=entity | source=src/sisalmacen/domain/auth.py:L77 | neighbors=[.get_by_id()] | lang=en
- "domain_auth_rationale_80": "Busca un usuario por nombre de acceso." | kind=entity | source=src/sisalmacen/domain/auth.py:L80 | neighbors=[.get_by_username()] | lang=en
- "domain_auth_rationale_83": "Crea un usuario nuevo." | kind=entity | source=src/sisalmacen/domain/auth.py:L83 | neighbors=[.add()] | lang=fr
- "domain_auth_rationale_86": "Persiste cambios de un usuario existente." | kind=entity | source=src/sisalmacen/domain/auth.py:L86 | neighbors=[.save()] | lang=en
- "domain_auth_rationale_89": "Obtiene un rol por su código." | kind=entity | source=src/sisalmacen/domain/auth.py:L89 | neighbors=[.get_role_by_code()] | lang=es
- "domain_auth_rationale_92": "Lista los roles disponibles." | kind=entity | source=src/sisalmacen/domain/auth.py:L92 | neighbors=[.list_roles()] | lang=es
- "domain_auth_rationale_95": "Lista los usuarios registrados." | kind=entity | source=src/sisalmacen/domain/auth.py:L95 | neighbors=[.list_users()] | lang=es
- "domain_auth_rationale_98": "Devuelve el total de administradores activos." | kind=entity | source=src/sisalmacen/domain/auth.py:L98 | neighbors=[.count_active_admins()] | lang=en
- "domain_errors_domainerror_init": ".__init__()" | kind=code-symbol | source=src/sisalmacen/domain/errors.py:L11 | neighbors=[DomainError] | lang=en
- "domain_errors_rationale_1": "Errores funcionales y de dominio." | kind=entity | source=src/sisalmacen/domain/errors.py:L1 | neighbors=[errors.py] | lang=en
- "domain_errors_rationale_7": "Base para errores funcionales con código estable." | kind=entity | source=src/sisalmacen/domain/errors.py:L7 | neighbors=[DomainError] | lang=es
- "domain_init": "__init__.py" | kind=code-symbol | source=src/sisalmacen/domain/__init__.py:L1 | neighbors=[Capa de dominio de SisAlmacen.] | lang=en
- "domain_init_rationale_1": "Capa de dominio de SisAlmacen." | kind=entity | source=src/sisalmacen/domain/__init__.py:L1 | neighbors=[__init__.py] | lang=nl
- "domain_repositories_rationale_1": "Protocolos base de repositorios del dominio." | kind=entity | source=src/sisalmacen/domain/repositories.py:L1 | neighbors=[repositories.py] | lang=en
- "domain_repositories_rationale_12": "Contrato mínimo para repositorios inyectables." | kind=entity | source=src/sisalmacen/domain/repositories.py:L12 | neighbors=[Repository] | lang=en
- "domain_repositories_rationale_15": "Agrega una entidad a la unidad de trabajo." | kind=entity | source=src/sisalmacen/domain/repositories.py:L15 | neighbors=[.add()] | lang=en
- "domain_repositories_rationale_18": "Obtiene una entidad por su identificador." | kind=entity | source=src/sisalmacen/domain/repositories.py:L18 | neighbors=[.get_by_id()] | lang=es
- "exception": "Exception" | kind=code-symbol | neighbors=[DomainError] | lang=en
- "infrastructure_config_rationale_1": "Resolución de rutas y configuración base de la aplicación." | kind=entity | source=src/sisalmacen/infrastructure/config.py:L1 | neighbors=[config.py] | lang=en
- "infrastructure_config_rationale_11": "Rutas utilizadas por la aplicación local." | kind=entity | source=src/sisalmacen/infrastructure/config.py:L11 | neighbors=[AppPaths] | lang=es
- "infrastructure_config_rationale_20": "Obtiene la raíz del proyecto en modo desarrollo." | kind=entity | source=src/sisalmacen/infrastructure/config.py:L20 | neighbors=[resolve_project_root()] | lang=es
- "infrastructure_config_rationale_26": "Construye las rutas persistentes principales." | kind=entity | source=src/sisalmacen/infrastructure/config.py:L26 | neighbors=[resolve_app_paths()] | lang=es
- "infrastructure_init": "__init__.py" | kind=code-symbol | source=src/sisalmacen/infrastructure/__init__.py:L1 | neighbors=[Infraestructura de SisAlmacen.] | lang=en
- "infrastructure_init_rationale_1": "Infraestructura de SisAlmacen." | kind=entity | source=src/sisalmacen/infrastructure/__init__.py:L1 | neighbors=[__init__.py] | lang=nl
- "infrastructure_logging_rationale_1": "Configuración de logging de SisAlmacen." | kind=entity | source=src/sisalmacen/infrastructure/logging.py:L1 | neighbors=[logging.py] | lang=nl
- "infrastructure_logging_rationale_11": "Configura logging rotativo sin exponer datos sensibles." | kind=entity | source=src/sisalmacen/infrastructure/logging.py:L11 | neighbors=[configure_logging()] | lang=en
- "integration_test_schema_reference_rationale_1": "Pruebas de equivalencia entre la migración y el SQL de referencia." | kind=entity | source=tests/integration/test_schema_reference.py:L1 | neighbors=[test_schema_reference.py] | lang=es
- "integration_test_schema_reference_test_initial_migration_loads_seed_data": "test_initial_migration_loads_seed_data()" | kind=code-symbol | source=tests/integration/test_schema_reference.py:L44 | neighbors=[test_schema_reference.py] | lang=en
- "integration_test_uow_test_sqlalchemy_uow_commit_persists_changes": "test_sqlalchemy_uow_commit_persists_changes()" | kind=code-symbol | source=tests/integration/test_uow.py:L14 | neighbors=[test_uow.py] | lang=en
- "integration_test_uow_test_sqlalchemy_uow_rollback_discards_changes": "test_sqlalchemy_uow_rollback_discards_changes()" | kind=code-symbol | source=tests/integration/test_uow.py:L34 | neighbors=[test_uow.py] | lang=en
- "qmainwindow": "QMainWindow" | kind=code-symbol | neighbors=[MainWindow] | lang=en

## Instructions

Write a single JSON object mapping each node id to a one-sentence description
to: c:\Users\friveraq\Downloads\SisAlmacen 1 (1)\SisAlmacen\SisAlmacen\.graphify\description-instructions\batch-009.json

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
