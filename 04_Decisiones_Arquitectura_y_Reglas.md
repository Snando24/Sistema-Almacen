# 04 — Decisiones de Arquitectura y Reglas de Negocio Cerradas

**Versión:** 1.0 · **Fecha:** 2026-10-03  
**Alcance:** Escenario A (local, una estación) con capas preparadas para evolucionar a multiusuario.  
**Uso:** este documento cierra las "Decisiones pendientes" de los documentos 01, 02 y 03 para poder iniciar el desarrollo. Las decisiones marcadas **[VALIDAR]** son supuestos razonables; se implementan con ese valor, pero deben confirmarse con el cliente antes del UAT. Si cambian, el impacto está indicado.

---

## 1. Decisiones de plataforma

| ID | Decisión | Motivo |
|---|---|---|
| ADR-01 | Se construye primero el **Escenario A (local)**. Multiusuario queda como evolución, no se implementa. | Decisión del proyecto. |
| ADR-02 | Lenguaje **Python 3.12**, UI **PySide6 (Qt 6)**, acceso a datos **SQLAlchemy 2.x**, migraciones **Alembic**, BD **SQLite**. | Stack elegido. |
| ADR-03 | Arquitectura en 4 capas: `ui` ? `application` ? `domain` ? `infrastructure`. La UI nunca importa SQLAlchemy ni toca la BD. | RNF-009, doc 03 §26. |
| ADR-04 | Repositorios definidos como `Protocol` en `domain`; implementados con SQLAlchemy en `infrastructure`. Casos de uso en `application` reciben un `UnitOfWork`. | Permite sustituir por API/PostgreSQL sin reescribir lógica. |
| ADR-05 | Excel con **openpyxl**, PDF con **reportlab**, CSV con `csv` estándar, hash de contraseñas con **argon2-cffi** (Argon2id). | Librerías maduras, sin dependencias externas de Office. |
| ADR-06 | Empaquetado con **PyInstaller** (modo carpeta) + instalador opcional (Inno Setup). Windows 10/11. | RNF-001. |
| ADR-07 | Calidad: `pytest`, `pytest-qt`, `ruff`, `mypy` (estricto en `domain` y `application`). | Doc 03 §25. |

## 2. Decisiones de datos

| ID | Decisión |
|---|---|
| ADR-10 | **Cantidades** como `INTEGER` escalado ×1000 (3 decimales). **Dinero** como `INTEGER` escalado ×10000. En `domain`/`application` se usa `decimal.Decimal`; la conversión vive en `TypeDecorator` de `infrastructure`. Nunca `float`. |
| ADR-11 | Fechas/horas de auditoría y movimientos en **UTC ISO-8601** (`YYYY-MM-DDTHH:MM:SSZ`); la UI muestra hora local. `fecha_movimiento` es fecha de negocio (`YYYY-MM-DD`). |
| ADR-12 | **Baja lógica** con `activo`; no hay borrado físico de productos, catálogos ni usuarios. |
| ADR-13 | `movimiento`, `detalle_movimiento` y `auditoria` son **inmutables** (triggers en SQL). Correcciones = movimiento compensatorio con `movimiento_origen_id`. |
| ADR-14 | Stock actual en `inventario` (1 fila por producto), actualizado **solo** por `MovimientoService` dentro de la misma transacción que inserta el movimiento y la auditoría. |
| ADR-15 | Todas las tablas editables incluyen `row_version` (control optimista); en local se incrementa pero no genera conflictos. Deja lista la migración a multiusuario. |
| ADR-16 | Un solo almacén. `ubicacion` es jerárquica (`padre_id`) y se asigna al producto (no hay stock por ubicación en el MVP). |
| ADR-17 | Conexión SQLite: `PRAGMA foreign_keys=ON`, `journal_mode=WAL`, `busy_timeout=5000`. Operaciones críticas con `BEGIN IMMEDIATE`. |
| ADR-18 | El esquema de referencia es [db/001_schema.sql](db/001_schema.sql) y [db/002_seed.sql](db/002_seed.sql). Alembic `0001_initial` debe producir un esquema equivalente. |

### Actualización R&R — modelo de productos (2026-10-03)

Este ajuste incorpora de forma explícita [05_Ajustes_Modelo_Producto_y_Categorias_RR.md](../05_Ajustes_Modelo_Producto_y_Categorias_RR.md), que complementa las decisiones anteriores para la operación actual de R&R.

- La categoría es un atributo explícito y editable del producto; los colores de Excel histórico no constituyen una regla de negocio.
- El código externo es opcional. Cuando no se informa, la aplicación conserva la restricción técnica de identificador único generando un código interno `LEGACY-…`.
- Se desactiva el uso operativo de stock máximo. La columna se mantiene por compatibilidad histórica, sin formularios, alertas ni reportes, hasta una migración de eliminación posterior.
- Se conserva temporalmente `unidad_medida` en el maestro: aún es necesaria para validar decimales y registrar movimientos. La unidad por presentación requiere una especificación de movimientos distinta antes de retirar esta relación.
- Se mantiene un único almacén y una ubicación por producto (ADR-16). Stock simultáneo por almacén/ubicación queda fuera del MVP y requerirá sustituir `inventario(producto_id)`.

## 3. Reglas de negocio cerradas (resuelven doc 01 §23)

| # | Pendiente original | Decisión | Estado | Impacto si cambia |
|---|---|---|---|---|
| 1 | Tipo de productos | Productos físicos genéricos; categoría explícita. La unidad se mantiene temporalmente para controlar movimientos y decimales. | VALIDAR | Medio. |
| 2 | Campos exactos del CSV | Ver [06_Especificacion_CSV.md](06_Especificacion_CSV.md). | VALIDAR con CSV real | Medio: mapeo de columnas. |
| 3 | Identificador único | `codigo` externo único cuando se informa (sin distinguir mayúsculas, con `trim`). Si falta, se genera `LEGACY-…` interno. | Actualizado R&R | Medio. |
| 4 | CSV crea productos | Sí, según modo de importación y permiso. | VALIDAR | Bajo. |
| 5 | Precios | Sí, opcionales; `usar_precios` los habilita. | VALIDAR | Bajo. |
| 6 | Lotes | No en MVP (P3). | VALIDAR | Alto: cambia el modelo de stock. |
| 7 | Vencimientos | No en MVP (P3). | VALIDAR | Alto. |
| 8 | Series | No en MVP (P3). | VALIDAR | Alto. |
| 9 | Reportes obligatorios | Los 7 de RF-093. | VALIDAR | Bajo. |
| 10 | Perfiles | ADMIN, OPERADOR, CONSULTA. Detalle en doc 07. | VALIDAR | Bajo. |
| 11 | Volumen de registros | Diseñar para 50 000 productos y 500 000 movimientos. | VALIDAR | Índices/paginación. |
| 12 | Movimientos diarios | Hasta 500/día. | VALIDAR | Bajo. |
| 13 | Ubicación de backups | Carpeta configurable (`backup.carpeta`), recomendación de copia externa. | Cerrado | — |
| 14 | Lector de barras | Fuera del MVP. El campo `codigo_barras` queda soportado; un lector tipo teclado funciona sin código extra. | Cerrado | — |
| 15 | Más de una PC | No en MVP; diseño preparado (ADR-03/04/15). | Cerrado | — |

## 4. Reglas de negocio operativas

- **RB-01** Stock negativo prohibido por defecto (`inventario.permitir_stock_negativo=0`). Con valor `1`, se permite pero la auditoría marca `stock_negativo=true`.
- **RB-02** Entradas/salidas: cantidad > 0. Productos con unidad sin decimales exigen cantidad entera.
- **RB-03** Ajuste (positivo o negativo): `motivo` obligatorio, permiso `movimientos.ajuste`.
- **RB-04** Los tipos de movimiento con `requiere_motivo=1` exigen motivo.
- **RB-05** Un producto inactivo no admite movimientos ni importación de stock; sí admite reactivación.
- **RB-06** Barras único solo entre activos; reactivar un producto cuyo barras ya lo usa uno activo falla con error funcional.
- **RB-07** El stock máximo queda fuera de la operación actual. Su dato histórico no se muestra ni participa en validaciones, alertas o reportes.
- **RB-08** Alertas: `SIN_STOCK` si `cantidad <= 0`; `BAJO_MINIMO` si `stock_minimo` definido y `cantidad <= stock_minimo` y `cantidad > 0`. Si no se configura mínimo, la UI muestra `Sin configurar` y no infiere un umbral. Se calculan por consulta; no se persisten.
- **RB-09** Valor de inventario = ? `cantidad × precio_compra` (productos activos con precio).
- **RB-10** Un usuario no puede desactivarse a sí mismo ni al último ADMIN activo.
- **RB-11** Bloqueo de cuenta tras `seguridad.max_intentos` fallos durante `seguridad.bloqueo_minutos`.
- **RB-12** (revisada) Modo local sin inicio de sesión ni registro de empresa: al arrancar se crea o reutiliza un usuario ADMIN local (`LocalSessionService`) para atribuir la auditoría, y se completan `empresa.nombre` y `backup.carpeta` por defecto. El login (`AuthenticationService`) queda disponible para la migración a multiusuario (doc 02).
- **RB-13** Contraseñas: longitud mínima configurable (8), Argon2id, nunca registradas en logs ni auditoría.
- **RB-14** Toda escritura de negocio (producto, catálogo, movimiento, importación, usuario, configuración, backup/restore) genera un registro de auditoría en la misma transacción.
- **RB-15** Reportes y exportaciones usan datos al momento de la generación y registran en auditoría la exportación (usuario, reporte, filtros).

## 5. Importación y respaldo (resumen; detalle en doc 06)

- **RI-01** Dos fases: *validar/previsualizar* (guarda `importacion` + `detalle_importacion`) y *aplicar* (re-valida contra el estado vigente y ejecuta todo en una transacción).
- **RI-02** Política de errores por defecto: **todo o nada** si hay filas con error. Opción "omitir filas con error" disponible para ADMIN.
- **RI-03** Hash SHA-256 del archivo; si ya fue aplicado antes, se advierte y requiere confirmación explícita.
- **RB-20** Backup: API de copia en línea de SQLite (`Connection.backup`), empaquetado `.zip` con `manifest.json` (versión de esquema, fecha, hash SHA-256 de la BD).
- **RB-21** Restauración: valida hash, `PRAGMA integrity_check`, versión de esquema compatible; hace un backup automático previo; exige confirmación y cierra sesiones/conexiones antes de reemplazar.
- **RB-22** Recordatorio al iniciar si pasaron más de `backup.recordatorio_dias` desde el último respaldo.

## 6. Manejo de errores y logging

- Jerarquía de errores de dominio: `DomainError` ? `ValidationError`, `PermissionDenied`, `NotFoundError`, `ConflictError`, `BusinessRuleViolation`. Cada una con `code` estable (ej. `STOCK_INSUFICIENTE`) y mensaje de usuario en español.
- La UI muestra solo el mensaje funcional; el detalle técnico va a `logs/sisalmacen.log` (rotativo, sin datos sensibles).
- Los casos de uso no capturan excepciones técnicas para ocultarlas; la capa UI las convierte en un mensaje genérico con identificador de incidente.

## 7. Evolución a multiusuario (no implementar ahora)

Cambios previstos: sustituir `infrastructure` local por cliente HTTP hacia una API que reutiliza `application` y `domain`; migrar SQLite ? PostgreSQL con Alembic; activar la verificación de `row_version` (RF-M021); añadir sesiones/tokens. Las decisiones ADR-03, 04, 14 y 15 existen para que este paso no requiera reescribir reglas.
