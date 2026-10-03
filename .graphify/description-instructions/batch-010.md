# Node Description Batch 11 of 11

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

- "security_init": "__init__.py" | kind=code-symbol | source=src/sisalmacen/infrastructure/security/__init__.py:L1 | neighbors=[Servicios de seguridad.] | lang=en
- "security_init_rationale_1": "Servicios de seguridad." | kind=entity | source=src/sisalmacen/infrastructure/security/__init__.py:L1 | neighbors=[__init__.py] | lang=nl
- "sisalmacen_init": "__init__.py" | kind=code-symbol | source=src/sisalmacen/__init__.py:L1 | neighbors=[Paquete principal de SisAlmacen.] | lang=en
- "sisalmacen_init_rationale_1": "Paquete principal de SisAlmacen." | kind=entity | source=src/sisalmacen/__init__.py:L1 | neighbors=[__init__.py] | lang=nl
- "tests_conftest_project_root": "project_root()" | kind=code-symbol | source=tests/conftest.py:L18 | neighbors=[conftest.py] | lang=en
- "tests_conftest_rationale_1": "Fixtures compartidas de pruebas." | kind=entity | source=tests/conftest.py:L1 | neighbors=[conftest.py] | lang=nl
- "ui_init": "__init__.py" | kind=code-symbol | source=src/sisalmacen/ui/__init__.py:L1 | neighbors=[Interfaz de usuario de SisAlmacen.] | lang=en
- "ui_init_rationale_1": "Interfaz de usuario de SisAlmacen." | kind=entity | source=src/sisalmacen/ui/__init__.py:L1 | neighbors=[__init__.py] | lang=nl
- "ui_main_window_mainwindow_show_section": "._show_section()" | kind=code-symbol | source=src/sisalmacen/ui/main_window.py:L78 | neighbors=[MainWindow] | lang=en
- "ui_theme_rationale_1": "Tema visual corporativo para la aplicación de Grupo Corporación." | kind=entity | source=src/sisalmacen/ui/theme.py:L1 | neighbors=[theme.py] | lang=es
- "ui_theme_rationale_21": "Devuelve la hoja de estilo con identidad industrial del logo de la empresa." | kind=entity | source=src/sisalmacen/ui/theme.py:L21 | neighbors=[get_brand_style_sheet()] | lang=en
- "unit_test_brand_theme_rationale_1": "Pruebas del branding corporativo de la aplicación." | kind=entity | source=tests/unit/test_brand_theme.py:L1 | neighbors=[test_brand_theme.py] | lang=en
- "unit_test_brand_theme_test_brand_palette_has_company_colors": "test_brand_palette_has_company_colors()" | kind=code-symbol | source=tests/unit/test_brand_theme.py:L6 | neighbors=[test_brand_theme.py] | lang=en
- "unit_test_brand_theme_test_brand_stylesheet_contains_expected_sections": "test_brand_stylesheet_contains_expected_sections()" | kind=code-symbol | source=tests/unit/test_brand_theme.py:L12 | neighbors=[test_brand_theme.py] | lang=en
- "unit_test_types_test_scaled_decimal_round_trip_preserves_precision": "test_scaled_decimal_round_trip_preserves_precision()" | kind=code-symbol | source=tests/unit/test_types.py:L12 | neighbors=[test_types.py] | lang=en
- "unitofwork": "UnitOfWork" | kind=code-symbol | neighbors=[SqlAlchemyUnitOfWork] | lang=en
- "userrepository": "UserRepository" | kind=code-symbol | neighbors=[SqlAlchemyUserRepository] | lang=en
- "versions_0001_initial_downgrade": "downgrade()" | kind=code-symbol | source=src/sisalmacen/infrastructure/migrations/versions/0001_initial.py:L45 | neighbors=[0001_initial.py] | lang=en
- "versions_0001_initial_rationale_1": "Migración inicial equivalente al SQL de referencia." | kind=entity | source=src/sisalmacen/infrastructure/migrations/versions/0001_initial.py:L1 | neighbors=[0001_initial.py] | lang=nl
- "db_002_seed": "002_seed.sql" | kind=code-symbol | source=install-test/_internal/db/002_seed.sql:L1 | lang=en

## Instructions

Write a single JSON object mapping each node id to a one-sentence description
to: c:\Users\friveraq\Downloads\SisAlmacen 1 (1)\SisAlmacen\SisAlmacen\.graphify\description-instructions\batch-010.json

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
