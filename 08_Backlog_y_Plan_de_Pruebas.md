# 08 — Backlog por Entregas y Plan de Pruebas

Convención: `HU-xx` = historia; prioridad P0–P3 según doc 03 §21. Cada historia cumple la Definition of Done del doc 03 §25. Referencias RF/RN apuntan al doc 01.

> **Estado de implementación:** las Entregas 0 a 6 están codificadas (servicios en `application/`, repositorios en `infrastructure/db/`, pantallas en `ui/pages/`) con pruebas en `tests/`. Pendiente de verificar en una PC con Python: `pytest -q`, UAT con datos reales (HU-09.3) y pruebas de rendimiento con 50 000 productos (HU-09.1). Diferidos por el modo local: HU-01.2/01.3/01.4 (login, cambio de contraseña y gestión de usuarios; el código existe pero la UI no los expone).

## 0. Entrega 0 — Base técnica (antes de funcionalidades)

| ID | Historia | Criterio de aceptación | Pri |
|---|---|---|---|
| HU-00.1 | Estructura del proyecto, `pyproject.toml`, `ruff`, `mypy`, `pytest` | `pytest` y `ruff` corren en verde sobre el esqueleto | P0 |
| HU-00.2 | Modelos SQLAlchemy + migración Alembic `0001_initial` equivalente a `db/001_schema.sql` + seed | Test que compara tablas/índices/triggers con los del SQL de referencia; la BD resultante pasa las consultas de doc 05 | P0 |
| HU-00.3 | `UnitOfWork`, repositorios base, `TypeDecorator` de cantidad/dinero | Round-trip `Decimal` sin pérdida (0.001 y 0.0001); sin `float` | P0 |
| HU-00.4 | Logging rotativo y jerarquía de errores | Un error técnico queda en log sin datos sensibles; la UI recibe mensaje funcional | P0 |
| HU-00.5 | Esqueleto de ventana principal y arranque | La app abre, crea BD si no existe y ejecuta migraciones | P0 |

## Entrega 1 — Núcleo (Épicas 1, 2, 3)

| ID | Historia | Criterios de aceptación clave | Ref. | Pri |
|---|---|---|---|---|
| HU-01.1 | Sesión local automática (sustituye al asistente de primer arranque) | Sin usuarios ? crea ADMIN local y completa `empresa.nombre`/`backup.carpeta`; con ADMIN activo lo reutiliza; sin pedir datos | RB-12 | P0 |
| HU-01.2 | Login/logout (diferido a multiusuario) | Credenciales inválidas rechazadas; bloqueo tras N intentos; usuario inactivo no entra; hash Argon2id | RF-001, RB-11/13 | P3 |
| HU-01.3 | Cambio de contraseña | Aplica política de longitud; invalida el flag `debe_cambiar_password` | RF-001 | P0 |
| HU-01.4 | Gestión de usuarios y roles | CRUD; no desactivar último ADMIN ni a sí mismo | RF-002/003, RB-10 | P0 |
| HU-01.5 | `AuthorizationService` | Sin permiso ? `SIN_PERMISO` en el caso de uso, no solo en la UI | RF-003 | P0 |
| HU-02.1 | Catálogos: categorías, marcas, unidades, proveedores, ubicaciones | Crear/editar/consultar/desactivar; nombre único; no desactivar si lo usa un producto activo (o advertir) | RF-020…024 | P0 |
| HU-03.1 | Alta de producto | Obligatorios, código único, barras único entre activos, min ? max | RF-010…012, RB-06/07 | P0 |
| HU-03.2 | Edición y detalle de producto | Cambios auditados con valor anterior/nuevo; `row_version` incrementa | RF-013/014 | P0 |
| HU-03.3 | Desactivar/reactivar | Conserva historial; reactivar valida barras | RF-015/016 | P0 |
| HU-03.4 | Listado con búsqueda y filtros básicos | Búsqueda por código/nombre/barras; paginado | RF-060 | P0 |
| HU-03.5 | Auditoría base (servicio) | Toda escritura de HU anteriores genera registro en la misma transacción | RB-14 | P0 |

## Entrega 2 — Inventario (Épica 4)

> Condición previa: confirmar lotes/vencimientos/series (doc 04, decisiones 6–8).

| ID | Historia | Criterios de aceptación clave | Ref. | Pri |
|---|---|---|---|---|
| HU-04.1 | `MovimientoService` | Insert movimiento + detalle + update inventario + auditoría en una transacción; fallo ? nada se persiste | RF-031/044, RB-14 | P0 |
| HU-04.2 | Entrada | Aumenta stock; guarda stock anterior/resultante | RF-040 | P0 |
| HU-04.3 | Salida | Disminuye; rechaza si deja negativo (según config) | RF-041, RB-01 | P0 |
| HU-04.4 | Ajuste | Motivo obligatorio; ± según diferencia | RF-042, RB-03 | P0 |
| HU-04.5 | Tipos de movimiento administrables | Los `es_sistema` no se desactivan | RF-043 | P1 |
| HU-04.6 | Historial por producto y global | Filtros por producto/tipo/fecha/usuario | RF-033 | P0 |
| HU-04.7 | Corrección compensatoria | Genera movimiento inverso enlazado; original intacto | RN-002, ADR-13 | P1 |
| HU-04.8 | Invariante de consistencia | Consulta doc 05 §3 devuelve 0 filas tras toda la suite | RN-003 | P0 |

## Entrega 3 — Datos masivos (Épica 5)

| ID | Historia | Criterios de aceptación clave | Ref. | Pri |
|---|---|---|---|---|
| HU-05.1 | Lectura CSV (codificación, separador, encabezado) | Casos del doc 06 §1 | RF-050 | P0 |
| HU-05.2 | Validación y clasificación de filas | Todos los códigos E01–E24 cubiertos con tests | RF-051 | P0 |
| HU-05.3 | Vista previa | Totales: total/nuevos/actualizables/errores | RF-052 | P0 |
| HU-05.4 | Aplicación transaccional con re-validación | Todo o nada; interrupción simulada deja BD intacta | RF-055/056, RI-01/02 | P0 |
| HU-05.5 | Opción "Aplicar stock" | Genera `ENT_INICIAL`/ajustes enlazados a `importacion_id` | doc 06 §3 | P1 |
| HU-05.6 | Exportar informe de errores | CSV con formato del doc 06 §5 | RF-057 | P0 |
| HU-05.7 | Historial y detección de archivo repetido | Resumen guardado; advertencia por hash | RF-058, RI-03 | P1 |
| HU-05.8 | Progreso en UI | Tarea en hilo; la UI no se congela con 50 000 filas | RNF-004 | P1 |

## Entrega 4 — Operación diaria (Épica 6 + filtros + dashboard)

| ID | Historia | Criterios | Ref. | Pri |
|---|---|---|---|---|
| HU-06.1 | Filtros avanzados combinables | Todos los de RF-061; limpiar filtros | RF-061…063 | P1 |
| HU-06.2 | Alertas (sin stock, bajo mínimo, sobre máximo) | Reglas RB-08 verificadas con tests de borde (=0, =mínimo, =máximo) | RF-070…072 | P1 |
| HU-06.3 | Dashboard | Indicadores RF-080 correctos; alertas navegan a listado filtrado | RF-080/081, RF-073 | P1 |

## Entrega 5 — Gestión (Épicas 7 y 8 parcial)

| ID | Historia | Criterios | Ref. | Pri |
|---|---|---|---|---|
| HU-07.1 | Exportar CSV | Listado completo y filtrado | RF-090 | P1 |
| HU-07.2 | Exportar Excel | Encabezados, formatos numérico/fecha, autofiltro, totales | RF-091 | P1 |
| HU-07.3 | Reportes (7) con filtros previos | Cada uno validado contra datos conocidos | RF-093/094 | P1 |
| HU-07.4 | PDF + vista previa/impresión | Logo, empresa, fecha, filtros, numeración de páginas | RF-092/095 | P1 |
| HU-08.1 | Pantalla de auditoría | Filtros y detalle JSON; solo lectura | RF-100…102 | P1 |
| HU-08.2 | Configuración | Datos de empresa y parámetros; cambios auditados | RF-120/121 | P1 |

## Entrega 6 — Cierre MVP

| ID | Historia | Criterios | Ref. | Pri |
|---|---|---|---|---|
| HU-08.3 | Backup manual | `.zip` con manifest y hash | RF-110, RB-20 | P1 |
| HU-08.4 | Restauración | Backup previo, validación, reemplazo, reinicio; prueba de restauración obligatoria | RF-111/112, RB-21 | P1 |
| HU-08.5 | Recordatorio de backup | Aviso según `backup.recordatorio_dias` | RB-22 | P2 |
| HU-09.1 | Pruebas integrales y de rendimiento | Plan §2 completo | doc 03 F13 | P0 |
| HU-09.2 | Empaquetado e instalador | Instala en Windows 10/11 limpio; crea BD y ADMIN | ADR-06 | P0 |
| HU-09.3 | UAT | Escenarios doc 03 §18 aprobados y acta | doc 03 F14 | P0 |

## 1. Orden de trabajo sugerido (hitos de cierre)

`E0 ? E1 ? E2 ? E3 ? E4 ? E5 ? E6`. No iniciar E3 sin invariante HU-04.8 verde; no iniciar E5 sin alertas y filtros estables.

## 2. Plan de pruebas

### Unitarias (dominio/aplicación, sin BD ni Qt)
- Cálculo de signo, stock resultante y rechazo de stock negativo (con y sin config).
- Validaciones de cantidad/decimales por unidad; cantidad 0 y negativa.
- Reglas de producto (min/max, barras, estado).
- Reglas de alertas con valores de borde.
- Clasificación de filas CSV (E01–E24), parseo de decimales `.` y `,`.
- Políticas de contraseña y bloqueo.

### Integración (SQLite real en memoria o archivo temporal)
- Migración `0001` = SQL de referencia; migración desde N?1.
- Triggers: no UPDATE/DELETE en `auditoria`/`movimiento`/`detalle_movimiento`; no mover inactivos.
- `MovimientoService`: rollback completo ante error simulado a mitad.
- Importación: éxito, error parcial (todo o nada vs. omitir), re-validación por cambio entre vista previa y confirmación, interrupción.
- Backup ? restaurar en BD de prueba ? comparar contenido y hash.
- Invariante stock = ? movimientos al final de cada prueba de inventario/importación.

### UI (pytest-qt, flujos críticos)
Login válido/ inválido · alta de producto con duplicado · salida con stock insuficiente · importación completa de `samples/productos_valido.csv` · importación de `samples/productos_con_errores.csv` (esperar los 9 errores E01–E09 correspondientes).

### Rendimiento (objetivos del doc 01 RNF-004)
- Listado con 50 000 productos: consulta paginada < 2 s.
- Búsqueda por código/nombre/barras < 2 s.
- Importación de 50 000 filas con progreso y sin congelar la UI.
- Reporte de movimientos sobre 500 000 registros con filtro de fechas < 5 s (objetivo, ajustar con cliente).

### UAT
Escenarios del doc 03 §18 ejecutados con datos reales del cliente; acta firmada.
