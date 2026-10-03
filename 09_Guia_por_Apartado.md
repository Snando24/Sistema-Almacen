# 09 — Guía de funcionamiento por apartado

Describe qué hace cada pantalla de **R&R Grupo Corporación · Sistema de Almacén**, cómo se usa y qué reglas aplica. Complementa los documentos 04 (reglas), 06 (CSV) y 07 (permisos).

## 1. Conceptos generales

### Modo local, sin inicio de sesión
- La aplicación abre directamente en el **Dashboard**. No hay login ni registro de empresa.
- Al arrancar se usa el primer usuario **ADMIN** activo; si no existe, se crea el usuario `local` (sin contraseña utilizable). Ese usuario figura en la auditoría y en los movimientos.
- Si faltan, se completan solos `empresa.nombre` (R&R Grupo Corporación) y `backup.carpeta` (`var/respaldos`). Se pueden cambiar en **Administración › Configuración**.

### Dónde se guardan los datos
| Qué | Dónde |
|---|---|
| Base de datos (SQLite) | `var/sisalmacen.sqlite3` |
| Registro técnico (errores) | `logs/sisalmacen.log` |
| Respaldos manuales | carpeta configurada, por defecto `var/respaldos` |
| Respaldos automáticos previos a una restauración | `var/respaldos/automaticos` |

### Navegación
Menú lateral con 7 secciones. Atajos: `Ctrl+1` … `Ctrl+7` (ir a cada sección), `F5` (actualizar la pantalla), `Ctrl+Q` (salir). Al entrar a una sección se recargan sus datos.

### Reglas que valen en toda la aplicación
- **El stock solo cambia mediante movimientos.** No existe edición directa de existencias.
- Los movimientos y la auditoría **no se editan ni se borran**; los errores se corrigen con un movimiento compensatorio.
- **Baja lógica:** productos, catálogos y tipos de movimiento se desactivan, nunca se eliminan.
- Las cantidades usan hasta 3 decimales y el dinero hasta 4; si la unidad no admite decimales (p. ej. UND), solo se aceptan enteros.
- Las fechas se guardan en UTC y se muestran en hora local.
- Cada escritura relevante deja un registro de auditoría en la misma transacción.
- Los errores se muestran con un mensaje en español; el detalle técnico va solo al log.

### Permisos
Los casos de uso validan el permiso, no solo se ocultan botones. En modo local la sesión es ADMIN (todos los permisos). Con otros roles (futuro multiusuario): OPERADOR (productos, entradas, salidas, importación, reportes), CONSULTA (solo lectura y reportes). Los botones sin permiso aparecen deshabilitados.

---

## 2. Dashboard
Resumen del almacén al momento de abrir o pulsar **Actualizar resumen**.

| Indicador | Qué cuenta |
|---|---|
| Productos / Activos | Total registrado y activos |
| Sin stock | Productos activos con stock 0 |
| Bajo el mínimo | Activos con stock > 0 y ? stock mínimo |
| Sobre el máximo | Activos con stock > máximo (solo si está activada la alerta de máximo) |
| Entradas / Salidas de hoy | Movimientos del día de cada naturaleza |
| Valor estimado | ? stock × precio de compra (solo si hay permiso de precios y la valorización está activa) |

- Las tarjetas de alerta tienen **Ver productos**: abre Productos ya filtrado por esa alerta.
- **Accesos rápidos:** Nuevo producto, Registrar entrada, Registrar salida, Importar CSV, Reportes (según permisos).
- Si pasó más de `backup.recordatorio_dias` desde el último respaldo (o nunca se hizo), aparece un aviso amarillo.

## 3. Productos
Lista paginada (50 por página) con el stock actual.

**Búsqueda y filtros (combinables):** texto (código, nombre o código de barras), estado (Activos/Inactivos/Todos), alerta, categoría, marca, proveedor, ubicación, rango de precio de venta y rango de fecha de registro. **Limpiar filtros** restablece todo.

**Colores de fila:** rojo claro = sin stock, amarillo = bajo mínimo, azul = sobre máximo, gris = inactivo.

**Acciones**
- **Nuevo producto / Editar:** formulario con código*, nombre*, categoría*, unidad*, código de barras, marca, proveedor, ubicación, precios, stock mínimo y máximo, descripción y observaciones. Antes de crear el primer producto debe existir al menos una categoría y una unidad (las unidades vienen de fábrica).
- **Detalle e historial:** ficha completa, alerta y los últimos 200 movimientos del producto. También con doble clic.
- **Desactivar / reactivar:** conserva el historial. Un producto inactivo no admite movimientos.
- **Exportar:** el listado actual (con sus filtros) a CSV, Excel o PDF.

**Reglas:** código único (sin distinguir mayúsculas); código de barras único solo entre productos activos (al reactivar se vuelve a validar); stock máximo ? mínimo; no se puede cambiar la unidad de un producto que ya tiene movimientos; sin permiso de precios, las columnas de precio se ocultan y no se modifican al editar.

## 4. Movimientos
Historial de todas las líneas de movimiento y registro de nuevas operaciones.

**Historial:** filtro por producto, tipo y rango de fechas; 100 líneas por página. Muestra cantidad con signo, stock anterior y resultante, usuario, motivo/documento y, si corresponde, a qué movimiento corrige.

**Registrar entrada / salida**
1. Elegir tipo (Compra, Venta, Consumo, Pérdida…), fecha, documento y motivo.
2. Buscar el producto (código, nombre o barras + Enter), escribir la cantidad y **Agregar línea**. Si repite un producto, se suma a la línea existente.
3. **Confirmar movimiento:** se guarda todo o nada y se muestra el stock antes ? después de cada producto.

**Ajustar inventario:** se indica el **stock contado**; el sistema calcula la diferencia y crea un ajuste positivo o negativo. El motivo es obligatorio. Si no hay diferencia no se registra nada.

**Corregir movimiento (solo ADMIN):** selecciona una línea, pide el motivo y crea un movimiento inverso enlazado. El original no cambia, y un movimiento solo puede corregirse una vez (ni corregir una corrección).

**Reglas:** cantidad > 0; stock negativo prohibido salvo que se active en Configuración; algunos tipos exigen motivo (p. ej. Pérdida); los productos inactivos no se pueden mover.

## 5. Importación CSV
Carga masiva de productos en dos fases: **validar** y luego **aplicar**.

**Pestaña Importar**
1. **Examinar** y elegir el archivo.
2. Opciones: codificación (automática, UTF-8, Windows-1252), separador (automático, `,` `;` tabulador `|`), decimal (`.` o `,`) y modo (insertar y actualizar / solo insertar / solo actualizar).
3. Casillas: *Crear catálogos faltantes*, *Aplicar stock* (genera movimientos) y *Omitir filas con error* (solo ADMIN).
4. **Validar archivo:** muestra totales (altas, actualizaciones, sin cambios, con error) y una tabla fila a fila con el detalle de cada error. Resalta en rojo las filas con error y avisa si el archivo ya se aplicó antes.
5. **Exportar errores:** genera un CSV con fila, código, columna, código de error, mensaje y valor original.
6. **Aplicar importación:** pide confirmación, vuelve a validar contra el estado actual y ejecuta todo en **una sola transacción** con barra de progreso. Si algo cambió desde la vista previa, muestra una nueva vista previa en lugar de aplicar. **Descartar** cancela.

**Columnas:** `codigo` (obligatoria siempre); para altas también `nombre`, `categoria`, `unidad`. Opcionales: `codigo_barras`, `descripcion`, `marca`, `proveedor`, `ubicacion`, `precio_compra`, `precio_venta`, `stock_minimo`, `stock_maximo`, `stock`, `estado`, `observaciones`. En actualización, una celda vacía significa «no modificar» y `[BORRAR]` limpia un campo opcional.

**Con *Aplicar stock*:** productos nuevos con stock > 0 generan una entrada inicial; productos existentes con stock distinto generan un ajuste por la diferencia. Todos quedan enlazados a la importación.

**Errores frecuentes:** E01 código vacío · E02 duplicado en el archivo · E03 dato obligatorio vacío · E04 catálogo inexistente · E05 número inválido · E06 máximo < mínimo · E07 decimales no permitidos · E08 valor negativo · E09 estado inválido · E10 texto demasiado largo · E11 código de barras repetido · E20/E21 modo no coincide · E22 cambio de unidad con movimientos · E23 producto inactivo con stock · E24 stock fuera de rango. Detalle completo en el doc 06.

**Política:** si hay errores no se aplica nada, salvo que un ADMIN marque *Omitir filas con error*.

**Pestaña Historial:** todas las importaciones con estado (VALIDADA, APLICADA, CANCELADA, FALLIDA), contadores y **Ver errores**.

## 6. Reportes
1. Elegir reporte y criterios; pulsar **Generar** para ver la tabla.
2. **Vista previa / imprimir** abre un PDF en el visor del sistema.
3. Exportar a **CSV, Excel o PDF** (el PDF lleva logo si está configurado, empresa, fecha, filtros y numeración de páginas).

| Reporte | Contenido | Criterios que usa |
|---|---|---|
| Inventario general | Todos los productos con stock, mínimo, máximo, precios y alerta | Categoría, incluir inactivos |
| Stock bajo | Productos bajo el mínimo | Categoría |
| Productos sin stock | Activos en cero | Categoría |
| Inventario por categoría | Productos, con stock y valor por categoría | — |
| Movimientos por período | Líneas de movimiento entre dos fechas (por defecto el mes en curso) | Desde, hasta, tipo |
| Historial de producto | Movimientos de un producto | Producto, fechas |
| Inventario valorizado | Stock × precio de compra con total | Categoría |

Cada exportación queda en la auditoría. El valorizado y las columnas de precio requieren permiso de precios y la opción de valorización activa.

## 7. Catálogos
Una pestaña por catálogo: **Categorías, Marcas, Unidades, Proveedores y Ubicaciones**.
- **Nuevo / Editar / Activar-desactivar**; **Mostrar inactivos** incluye los dados de baja.
- Nombre (o código) único sin distinguir mayúsculas.
- No se puede desactivar un registro que usan productos activos.
- **Unidades:** la casilla *Permite decimales* define si los productos de esa unidad admiten cantidades fraccionarias (UND, CAJ y PAQ no; KG, LT y MT sí).
- **Ubicaciones:** pueden tener una ubicación padre; se rechazan jerarquías circulares.

## 8. Administración
Cuatro pestañas (se muestran según permisos).

### Auditoría
Bitácora de solo lectura, más reciente primero, 100 por página. Filtros por fecha, usuario, entidad y acción (CREAR, EDITAR, DESACTIVAR, ENTRADA, SALIDA, AJUSTE, IMPORTAR, EXPORTAR, CONFIGURAR, RESPALDAR…). Al seleccionar una fila se ven el valor anterior y el nuevo en JSON.

### Configuración
- **Empresa:** nombre (obligatorio), RUC, dirección, teléfono y logo (png/jpg) usados en los PDF y Excel.
- **Inventario:** permitir stock negativo, alertar sobre stock máximo, gestionar precios y valorización, moneda.
- **Importación:** máximo de filas por CSV (50 000 por defecto).
- **Respaldos:** carpeta y días para el recordatorio.
Solo se guardan (y auditan) los valores que cambian.

### Tipos de movimiento
Crear, renombrar, marcar *Exige motivo* y activar/desactivar tipos. Los de sistema (ingreso inicial, ajustes) no se pueden desactivar. La naturaleza (entrada, salida, ajuste positivo o negativo) define el signo y no se puede cambiar después de crear el tipo.

### Respaldos
- **Crear respaldo ahora:** genera un `.zip` en la carpeta configurada con la base de datos y un `manifest.json` (versión de esquema, fecha y hash SHA-256). Se puede elegir otra carpeta.
- **Restaurar respaldo:** pide confirmación (reemplaza **toda** la información actual), valida el archivo (hash, integridad e versión), guarda antes un respaldo automático de la base actual, reemplaza la base y **cierra la aplicación** para reiniciarla.
- Se recomienda copiar los respaldos a una unidad externa.

---

## 9. Problemas habituales
| Síntoma | Causa y solución |
|---|---|
| «Cree al menos una categoría y una unidad…» al guardar un producto | Crear una categoría en Catálogos |
| «Stock insuficiente» en una salida | La cantidad supera el stock; registrar antes una entrada o activar stock negativo en Configuración |
| Importación rechazada con `CSV_CON_ERRORES` | Corregir el archivo, exportar el informe de errores o (ADMIN) omitir filas con error |
| «Los datos cambiaron desde la vista previa» | Alguien modificó productos entre validar y aplicar; revisar la nueva vista previa y volver a aplicar |
| «El respaldo no es válido» | Archivo dañado, modificado o de una versión incompatible; usar otro respaldo |
| Error técnico genérico | Revisar `logs/sisalmacen.log` |
