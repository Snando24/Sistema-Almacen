# Node Description Batch 3 of 11

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
Write every description in Spanish (es). Do not switch languages.
No marketing language.
Respond ONLY with a JSON object mapping each node id (as a string) to its
one-sentence description — no prose, no markdown fences.

- "application_auth_rationale_41": "Datos requeridos para el primer arranque." | kind=entity | source=src/sisalmacen/application/auth.py:L41 | neighbors=[InitialAdminPayload, BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError]
- "application_auth_rationale_429": "Actualiza datos básicos, rol y estado lógico de un usuario." | kind=entity | source=src/sisalmacen/application/auth.py:L429 | neighbors=[.update_user(), BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError]
- "application_auth_rationale_464": "Reinicia la contraseña de un usuario y fuerza cambio al ingresar." | kind=entity | source=src/sisalmacen/application/auth.py:L464 | neighbors=[.reset_password(), BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError]
- "application_auth_rationale_53": "Datos para crear un usuario desde administración." | kind=entity | source=src/sisalmacen/application/auth.py:L53 | neighbors=[CreateUserPayload, BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError]
- "application_auth_rationale_558": "Obtiene el resumen mostrado al entrar a la aplicación." | kind=entity | source=src/sisalmacen/application/auth.py:L558 | neighbors=[DashboardService, BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError]
- "application_auth_rationale_564": "Devuelve el estado agregado del sistema local." | kind=entity | source=src/sisalmacen/application/auth.py:L564 | neighbors=[.get_snapshot(), BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError]
- "application_auth_rationale_66": "Datos editables de un usuario existente." | kind=entity | source=src/sisalmacen/application/auth.py:L66 | neighbors=[UpdateUserPayload, BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError]
- "application_auth_rationale_77": "Datos para reinicio administrativo de contraseña." | kind=entity | source=src/sisalmacen/application/auth.py:L77 | neighbors=[ResetUserPasswordPayload, BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError]
- "application_auth_rationale_86": "Puerto mínimo del servicio de hash de contraseñas." | kind=entity | source=src/sisalmacen/application/auth.py:L86 | neighbors=[PasswordHasherPort, BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError]
- "application_auth_rationale_96": "Gestiona el primer arranque del sistema local." | kind=entity | source=src/sisalmacen/application/auth.py:L96 | neighbors=[InitialSetupService, BusinessRuleViolation, ConflictError, NotFoundError, PermissionDenied, ValidationError]
- "application_auth_usermanagementservice_create_user": ".create_user()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L387 | neighbors=[Crea un usuario con contraseña temporal…, UserManagementService, .require_permission(), ._ensure_username_available(), ._require_role(), ._validate_password_policy()]
- "db_001_schema_detalle_movimiento": "detalle_movimiento" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L200 | neighbors=[001_schema.sql, movimiento, producto, trg_detmov_no_delete, trg_detmov_no_update, trg_detmov_producto_activo]
- "db_001_schema_usuario": "usuario" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L37 | neighbors=[001_schema.sql, auditoria, importacion, movimiento, producto, rol]
- "db_bootstrap": "bootstrap.py" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/bootstrap.py:L1 | neighbors=[_bootstrap_sql_files(), build_alembic_config(), _database_has_tables(), _resolve_runtime_path(), run_migrations(), Inicialización de la base de datos y mi…]
- "db_bootstrap_run_migrations": "run_migrations()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/bootstrap.py:L80 | neighbors=[bootstrap.py, Aplica todas las migraciones pendientes…, _bootstrap_sql_files(), build_alembic_config(), _database_has_tables(), _resolve_runtime_path()]
- "integration_test_auth_services_test_user_management_reset_password_forces_change_and_unlocks": "test_user_management_reset_password_forces_change_and_unlocks()" | kind=code-symbol | source=tests/integration/test_auth_services.py:L310 | neighbors=[test_auth_services.py, _build_session_factory(), _create_operator(), _lock_user(), _login_as_admin(), _seed_admin()]
- "sisalmacen_main_main": "main()" | kind=code-symbol | source=src/sisalmacen/main.py:L33 | neighbors=[main.py, _build_dashboard_loader(), _build_initial_setup_handler(), _build_login_handler(), _requires_initial_setup(), Inicia la aplicación de escritorio.]
- "versions_0001_initial": "0001_initial.py" | kind=code-symbol | source=src/sisalmacen/infrastructure/migrations/versions/0001_initial.py:L1 | neighbors=[downgrade(), _repo_root(), _run_script(), _sqlite_connection(), upgrade(), Migración inicial equivalente al SQL de…]
- "application_auth_usermanagementservice_reset_password": ".reset_password()" | kind=code-symbol | source=src/sisalmacen/application/auth.py:L463 | neighbors=[Reinicia la contraseña de un usuario y …, UserManagementService, .require_permission(), ._require_user(), ._validate_password_policy()]
- "db_bootstrap_bootstrap_sql_files": "_bootstrap_sql_files()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/bootstrap.py:L60 | neighbors=[bootstrap.py, _database_has_tables(), _resolve_runtime_path(), Crea la Base de Datos desde los SQL de …, run_migrations()]
- "db_bootstrap_resolve_runtime_path": "_resolve_runtime_path()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/bootstrap.py:L13 | neighbors=[bootstrap.py, _bootstrap_sql_files(), build_alembic_config(), Resuelve la ruta real de archivos de re…, run_migrations()]
- "db_models_auditoria": "Auditoria" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/models.py:L285 | neighbors=[models.py, Base, Base, ScaledMoney, ScaledQuantity]
- "db_models_detalleimportacion": "DetalleImportacion" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/models.py:L225 | neighbors=[models.py, Base, Base, ScaledMoney, ScaledQuantity]
- "db_models_detallemovimiento": "DetalleMovimiento" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/models.py:L262 | neighbors=[models.py, Base, Base, ScaledMoney, ScaledQuantity]
- "db_models_importacion": "Importacion" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/models.py:L201 | neighbors=[models.py, Base, Base, ScaledMoney, ScaledQuantity]
- "db_models_inventario": "Inventario" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/models.py:L178 | neighbors=[models.py, Base, Base, ScaledMoney, ScaledQuantity]
- "db_models_marca": "Marca" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/models.py:L85 | neighbors=[models.py, Base, Base, ScaledMoney, ScaledQuantity]
- "db_models_proveedor": "Proveedor" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/models.py:L107 | neighbors=[models.py, Base, Base, ScaledMoney, ScaledQuantity]
- "db_models_ubicacion": "Ubicacion" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/models.py:L121 | neighbors=[models.py, Base, Base, ScaledMoney, ScaledQuantity]
- "db_models_unidadmedida": "UnidadMedida" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/models.py:L94 | neighbors=[models.py, Base, Base, ScaledMoney, ScaledQuantity]
- "domain_auth_configurationrepository": "ConfigurationRepository" | kind=code-symbol | source=src/sisalmacen/domain/auth.py:L104 | neighbors=[auth.py, .get_many(), .set_many(), Protocol, Puerto para configuración persistente.]
- "integration_test_auth_services_build_current_session": "_build_current_session()" | kind=code-symbol | source=tests/integration/test_auth_services.py:L425 | neighbors=[test_auth_services.py, test_authorization_service_accepts_exis…, test_authorization_service_denies_missi…, test_user_management_rejects_deactivati…, test_user_management_rejects_missing_pe…]
- "integration_test_auth_services_test_change_password_updates_hash_and_clears_flag": "test_change_password_updates_hash_and_clears_flag()" | kind=code-symbol | source=tests/integration/test_auth_services.py:L116 | neighbors=[test_auth_services.py, _build_session_factory(), _mark_password_change_required(), _require_admin_id(), _seed_admin()]
- "integration_test_auth_services_test_user_management_rejects_deactivating_last_admin": "test_user_management_rejects_deactivating_last_admin()" | kind=code-symbol | source=tests/integration/test_auth_services.py:L284 | neighbors=[test_auth_services.py, _build_current_session(), _build_session_factory(), _require_admin_id(), _seed_admin()]
- "integration_test_schema_reference": "test_schema_reference.py" | kind=code-symbol | source=tests/integration/test_schema_reference.py:L1 | neighbors=[_execute_script(), _schema_snapshot(), test_initial_migration_loads_seed_data(), test_initial_migration_matches_referenc…, Pruebas de equivalencia entre la migrac…]
- "ui_main_window_mainwindow_setup_ui": "._setup_ui()" | kind=code-symbol | source=src/sisalmacen/ui/main_window.py:L54 | neighbors=[MainWindow, .__init__(), ._build_content(), ._build_menu(), ._build_sidebar()]
- "db_001_schema_auditoria": "auditoria" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L215 | neighbors=[001_schema.sql, usuario, trg_auditoria_no_delete, trg_auditoria_no_update]
- "db_001_schema_importacion": "importacion" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L154 | neighbors=[001_schema.sql, detalle_importacion, usuario, movimiento]
- "db_001_schema_ubicacion": "ubicacion" | kind=code-symbol | source=install-test/_internal/db/001_schema.sql:L90 | neighbors=[001_schema.sql, producto, ubicacion]
- "db_auth_repositories_sqlalchemyuserrepository_scalar": "._scalar()" | kind=code-symbol | source=src/sisalmacen/infrastructure/db/auth_repositories.py:L152 | neighbors=[SqlAlchemyUserRepository, .count_active_admins(), .count_active_users(), .count_users()]

## Instructions

Write a single JSON object mapping each node id to a one-sentence description
to: c:\Users\friveraq\Downloads\SisAlmacen 1 (1)\SisAlmacen\SisAlmacen\.graphify\description-instructions\batch-002.json

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
