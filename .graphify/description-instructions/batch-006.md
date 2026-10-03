# Node Description Batch 7 of 11

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

- "domain_auth_dashboardsnapshot": "DashboardSnapshot" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L54 | neighbors=[auth.py, Resumen para la pantalla inicial local.] | lang=en
- "domain_auth_roleinfo": "RoleInfo" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L29 | neighbors=[auth.py, Rol disponible en el sistema.] | lang=en
- "domain_auth_userrepository_add": ".add()" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L82 | neighbors=[Crea un usuario nuevo., UserRepository] | lang=en
- "domain_auth_userrepository_count_active_admins": ".count_active_admins()" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L97 | neighbors=[Devuelve el total de administradores ac…, UserRepository] | lang=en
- "domain_auth_userrepository_count_active_users": ".count_active_users()" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L73 | neighbors=[Devuelve el total de usuarios activos., UserRepository] | lang=en
- "domain_auth_userrepository_count_users": ".count_users()" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L70 | neighbors=[Devuelve el total de usuarios., UserRepository] | lang=en
- "domain_auth_userrepository_get_by_id": ".get_by_id()" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L76 | neighbors=[Busca un usuario por identificador., UserRepository] | lang=en
- "domain_auth_userrepository_get_by_username": ".get_by_username()" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L79 | neighbors=[Busca un usuario por nombre de acceso., UserRepository] | lang=en
- "domain_auth_userrepository_get_role_by_code": ".get_role_by_code()" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L88 | neighbors=[Obtiene un rol por su código., UserRepository] | lang=en
- "domain_auth_userrepository_list_permission_codes": ".list_permission_codes()" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L100 | neighbors=[Lista permisos asignados a un rol., UserRepository] | lang=en
- "domain_auth_userrepository_list_roles": ".list_roles()" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L91 | neighbors=[Lista los roles disponibles., UserRepository] | lang=en
- "domain_auth_userrepository_list_users": ".list_users()" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L94 | neighbors=[Lista los usuarios registrados., UserRepository] | lang=en
- "domain_auth_userrepository_save": ".save()" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L85 | neighbors=[Persiste cambios de un usuario existent…, UserRepository] | lang=en
- "domain_auth_usersummary": "UserSummary" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L38 | neighbors=[auth.py, Resumen de usuario para administración.] | lang=en
- "domain_repositories": "repositories.py" | kind=code-symbol | source=src/sisalmacen/domain/repositories.py:L1 | neighbors=[Repository, Protocolos base de repositorios del dom…] | lang=en
- "domain_repositories_repository_add": ".add()" | kind=code-symbol | source=src/sisalmacen/domain/repositories.py:L14 | neighbors=[Agrega una entidad a la unidad de traba…, Repository] | lang=en
- "domain_repositories_repository_get_by_id": ".get_by_id()" | kind=code-symbol | source=src/sisalmacen/domain/repositories.py:L17 | neighbors=[Obtiene una entidad por su identificado…, Repository] | lang=en
- "infrastructure_logging": "logging.py" | kind=code-symbol | source=src/sisalmacen/infrastructure/logging.py:L1 | neighbors=[configure_logging(), Configuración de logging de SisAlmacen.] | lang=en
- "infrastructure_logging_configure_logging": "configure_logging()" | kind=code-symbol | source=src/sisalmacen/infrastructure/logging.py:L10 | neighbors=[logging.py, Configura logging rotativo sin exponer …] | lang=en
- "integration_test_auth_services_create_operator": "_create_operator()" | kind=code-symbol | source=tests/integration/test_auth_services.py:L367 | neighbors=[test_auth_services.py, test_user_management_reset_password_for…] | lang=en
- "integration_test_auth_services_lock_user": "_lock_user()" | kind=code-symbol | source=tests/integration/test_auth_services.py:L392 | neighbors=[test_auth_services.py, test_user_management_reset_password_for…] | lang=en
- "integration_test_auth_services_mark_password_change_required": "_mark_password_change_required()" | kind=code-symbol | source=tests/integration/test_auth_services.py:L401 | neighbors=[test_auth_services.py, test_change_password_updates_hash_and_c…] | lang=en
- "integration_test_auth_services_test_authorization_service_accepts_existing_permission": "test_authorization_service_accepts_existing_permission()" | kind=code-symbol | source=tests/integration/test_auth_services.py:L190 | neighbors=[test_auth_services.py, _build_current_session()] | lang=en
- "integration_test_auth_services_test_authorization_service_denies_missing_permission": "test_authorization_service_denies_missing_permission()" | kind=code-symbol | source=tests/integration/test_auth_services.py:L180 | neighbors=[test_auth_services.py, _build_current_session()] | lang=en
- "integration_test_auth_services_test_initial_setup_creates_admin_and_company_config": "test_initial_setup_creates_admin_and_company_config()" | kind=code-symbol | source=tests/integration/test_auth_services.py:L35 | neighbors=[test_auth_services.py, _build_session_factory()] | lang=en
- "integration_test_schema_reference_execute_script": "_execute_script()" | kind=code-symbol | source=tests/integration/test_schema_reference.py:L11 | neighbors=[test_schema_reference.py, test_initial_migration_matches_referenc…] | lang=en
- "integration_test_schema_reference_schema_snapshot": "_schema_snapshot()" | kind=code-symbol | source=tests/integration/test_schema_reference.py:L16 | neighbors=[test_schema_reference.py, test_initial_migration_matches_referenc…] | lang=en
- "integration_test_uow_rationale_1": "Pruebas mínimas de la unidad de trabajo." | kind=entity | source=tests/integration/test_uow.py:L1 | neighbors=[Configuracion, test_uow.py] | lang=nl
- "migrations_env_rationale_1": "Entorno Alembic para SisAlmacen." | kind=entity | source=src/sisalmacen/infrastructure/migrations/env.py:L1 | neighbors=[Base, env.py] | lang=en
- "migrations_env_rationale_22": "Ejecuta migraciones en modo offline." | kind=entity | source=src/sisalmacen/infrastructure/migrations/env.py:L22 | neighbors=[Base, run_migrations_offline()] | lang=en
- "migrations_env_rationale_37": "Ejecuta migraciones en modo online." | kind=entity | source=src/sisalmacen/infrastructure/migrations/env.py:L37 | neighbors=[Base, run_migrations_online()] | lang=en
- "migrations_env_run_migrations_offline": "run_migrations_offline()" | kind=code-symbol | source=src/sisalmacen/infrastructure/migrations/env.py:L21 | neighbors=[env.py, Ejecuta migraciones en modo offline.] | lang=en
- "migrations_env_run_migrations_online": "run_migrations_online()" | kind=code-symbol | source=src/sisalmacen/infrastructure/migrations/env.py:L36 | neighbors=[env.py, Ejecuta migraciones en modo online.] | lang=en
- "qdialog": "QDialog" | kind=code-symbol | neighbors=[InitialSetupDialog, LoginDialog] | lang=en
- "sisalmacen_bootstrap_rationale_1": "Bootstrap principal de la aplicación." | kind=entity | source=src/sisalmacen/bootstrap.py:L1 | neighbors=[AppPaths, bootstrap.py] | lang=en
- "sisalmacen_bootstrap_rationale_18": "Dependencias principales de ejecución." | kind=entity | source=src/sisalmacen/bootstrap.py:L18 | neighbors=[AppPaths, AppContext] | lang=nl
- "sisalmacen_bootstrap_rationale_26": "Prepara rutas, logging, migraciones y conexión a la BD." | kind=entity | source=src/sisalmacen/bootstrap.py:L26 | neighbors=[AppPaths, bootstrap_application()] | lang=es
- "sisalmacen_main_build_dashboard_loader": "_build_dashboard_loader()" | kind=code-symbol | source=src/sisalmacen/main.py:L146 | neighbors=[main.py, main()] | lang=en
- "sisalmacen_main_build_initial_setup_handler": "_build_initial_setup_handler()" | kind=code-symbol | source=src/sisalmacen/main.py:L101 | neighbors=[main.py, main()] | lang=en
- "sisalmacen_main_build_login_handler": "_build_login_handler()" | kind=code-symbol | source=src/sisalmacen/main.py:L123 | neighbors=[main.py, main()] | lang=en

## Instructions

Write a single JSON object mapping each node id to a one-sentence description
to: c:\Users\friveraq\Downloads\SisAlmacen 1 (1)\SisAlmacen\SisAlmacen\.graphify\description-instructions\batch-006.json

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
