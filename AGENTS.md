# AGENTS.md — Sistema de Gestión de Almacén (SisAlmacen)

Instrucciones para agentes de código (Copilot u otros) y desarrolladores. Leer antes de generar código.

## Contexto
Aplicación de escritorio para Windows 10/11, **escenario local (una estación)**, con diseño preparado para migrar a multiusuario. Idioma de UI, mensajes y documentación: **español**. Nombres de código (clases, funciones, variables): inglés para infraestructura, y términos de dominio en español cuando coincidan con el esquema (`producto`, `movimiento`).

## Documentos (fuente de verdad, en este orden)
1. [04_Decisiones_Arquitectura_y_Reglas.md](04_Decisiones_Arquitectura_y_Reglas.md) — decisiones y reglas cerradas.
2. [db/001_schema.sql](db/001_schema.sql), [db/002_seed.sql](db/002_seed.sql), [05_Modelo_de_Datos.md](05_Modelo_de_Datos.md) — modelo.
3. [06_Especificacion_CSV.md](06_Especificacion_CSV.md) — importación.
4. [07_Permisos_CasosUso_Pantallas.md](07_Permisos_CasosUso_Pantallas.md) — permisos, pantallas, mensajes.
5. [08_Backlog_y_Plan_de_Pruebas.md](08_Backlog_y_Plan_de_Pruebas.md) — qué construir y en qué orden.
6. Requerimientos originales: 01, 02 y 03.

Si un documento y el código discrepan, se corrige uno de los dos de forma explícita; no se resuelve en silencio.

## Stack
Python 3.12 · PySide6 · SQLAlchemy 2.x · Alembic · SQLite · argon2-cffi · openpyxl · reportlab · pytest/pytest-qt · ruff · mypy · PyInstaller. Dependencias en [pyproject.toml](pyproject.toml).

## Estructura objetivo
```text
src/sisalmacen/
  domain/           # entidades, value objects, reglas, errores, Protocols de repositorio (sin SQLAlchemy ni Qt)
  application/      # casos de uso/servicios, DTOs, UnitOfWork, AuthorizationService
  infrastructure/
    db/             # modelos SQLAlchemy, TypeDecorators, sesión, repositorios
    migrations/     # Alembic (0001_initial = db/001_schema.sql + seed)
    csv/            # lectura y validación de CSV
    export/         # Excel, PDF
    backup/         # backup/restauración
    security/       # Argon2id
  ui/               # PySide6: ventanas, modelos de tabla, workers
  main.py
tests/{unit,integration,ui}/
db/                 # SQL de referencia
samples/            # CSV de ejemplo
```
Dependencias permitidas: `ui ? application ? domain`; `infrastructure ? domain` (implementa Protocols); `application` no importa `infrastructure` (se inyecta). `domain` no importa nada del proyecto fuera de sí mismo.

## Reglas inquebrantables
1. **El stock solo cambia vía `MovimientoService`**, en la misma transacción que inserta `movimiento` + `detalle_movimiento` y la auditoría. Nunca `UPDATE inventario` desde otro sitio.
2. **`movimiento`, `detalle_movimiento` y `auditoria` no se actualizan ni eliminan.** Correcciones = movimiento compensatorio.
3. **Nunca `float`** para cantidades ni dinero: `Decimal` en código, enteros escalados (×1000 / ×10000) en BD vía `TypeDecorator`.
4. **La UI no accede a la BD ni a SQLAlchemy.** Los permisos se validan en `application`, no solo ocultando botones.
5. **Importar CSV = validar ? previsualizar ? confirmar ? re-validar ? aplicar en una transacción.** Nunca escribir directo.
6. **Baja lógica**, nunca borrado físico de productos/catálogos/usuarios.
7. **Contraseñas**: Argon2id; jamás en logs ni auditoría.
8. **SQL parametrizado**/ORM siempre; sin concatenar entradas del usuario.
9. Cada conexión SQLite activa `foreign_keys=ON`, `WAL`, `busy_timeout`; operaciones críticas con `BEGIN IMMEDIATE`.
10. Fechas en UTC en BD; la UI formatea a hora local.

## Flujo de trabajo
- Seguir el backlog de [08](08_Backlog_y_Plan_de_Pruebas.md) por entregas; **empezar por la Entrega 0**.
- Cada historia: pruebas primero para reglas críticas, luego implementación, luego UI.
- Definition of Done: ver doc 03 §25. Incluye validaciones, errores funcionales con código estable (doc 07 §5), auditoría y tests.
- Commits pequeños y convencionales (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`), rama `main` + ramas `feature/<hu>`.
- No añadir funcionalidades fuera del MVP (múltiples almacenes, lotes, ventas, web/móvil) sin actualizar antes el doc 04.

## Comandos (tras crear el entorno)
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
ruff check . ; ruff format --check .
mypy src/sisalmacen/domain src/sisalmacen/application
pytest -q
alembic upgrade head
sisalmacen
```

## Primeras tareas para la nueva PC
1. Crear repo Git, copiar esta carpeta (docs, `db/`, `samples/`, `AGENTS.md`, `pyproject.toml`).
2. **Validar** `db/001_schema.sql` + `db/002_seed.sql` ejecutándolos en SQLite 3.35+ (no se ejecutaron en la PC de preparación): `sqlite3 :memory: ".read db/001_schema.sql" ".read db/002_seed.sql"`.
3. Crear el esqueleto de `src/sisalmacen/` y la Entrega 0.
4. Obtener un **CSV real** del cliente y comparar con doc 06; ajustar columnas.
5. Resolver con el cliente los puntos **[VALIDAR]** del doc 04 (especialmente 3, 6, 7, 8) antes de la Entrega 2.
