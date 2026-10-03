# Cambios Realizados - Sistema de Almacén

## Resumen Ejecutivo

Se han completado **cuatro prioridades** de cambios alineados con los documentos de especificación:

1. **Prioridad 1**: Remover `stock_maximo` del modelo (14 archivos, 59 referencias)
2. **Prioridad 2**: Normalizar nomenclatura de alertas: `ALERT_SIN_STOCK` ? `ALERT_AGOTADO` (7 archivos)
3. **Prioridad 3**: Crear infraestructura CSV de exportación (nuevo módulo, métodos en servicios)
4. **Prioridad 4**: Agregar botones UI y funcionalidad de importación/exportación (2 páginas, 1 nuevo diálogo)

---

## Prioridad 1: Remover `stock_maximo` ?

### Justificación
El modelo R&R actual no utiliza stock máximo. Es un legado de la versión anterior que genera confusión y ocupa espacio en BD/código.

### Archivos modificados (14)

#### Domain Layer
- `src/sisalmacen/domain/inventory.py`
  - Removidas constantes: `ALERT_SOBRE_MAXIMO`
  - Actualizado: `compute_alert(cantidad, stock_minimo)` (parámetro `stock_maximo` eliminado)
  - Actualizado: `ProductData` dataclass (sin campo `stock_maximo`)
  - Actualizado: `ProductRecord` (sin stock_maximo)
  - Actualizado: `ProductFilter` (sin usar_stock_maximo)

- `src/sisalmacen/domain/auth.py`
  - Actualizado: `DashboardSnapshot` (removido campo `productos_sobre_maximo`)

- `src/sisalmacen/domain/importing.py`
  - Actualizado: `ExistingProduct` dataclass (sin stock_maximo)

#### Application Layer
- `src/sisalmacen/application/products.py`
  - Removida validación: `stock_maximo < stock_minimo`
  - Actualizado: método `search()` (sin usar_stock_maximo)

- `src/sisalmacen/application/reports.py`
  - Actualizado: `_product_table()` (simplificada llamada a `item.alert()`)

- `src/sisalmacen/application/settings.py`
  - Removido: SettingSpec para "inventario.usar_stock_maximo"

- `src/sisalmacen/application/importing.py`
  - Removida lógica de stock_maximo

#### Infrastructure Layer
- `src/sisalmacen/infrastructure/db/models.py`
  - Removida columna `stock_maximo` del modelo ORM `Producto`
  - Removida constraint CHECK

- `db/001_schema.sql`
  - Removida columna `stock_maximo` de tabla `producto`
  - Removida constraint CHECK

- `src/sisalmacen/infrastructure/db/catalog_product_repositories.py`
  - Actualizado: `alert_conditions()` (sin SOBRE_MAXIMO)
  - Actualizado: `_to_record()` (no mapea stock_maximo)

- `src/sisalmacen/infrastructure/db/import_settings_repositories.py`
  - Actualizado: `build_dashboard_snapshot()` (sin productos_sobre_maximo)

#### UI Layer
- `src/sisalmacen/ui/pages/dashboard_page.py`
  - Removida tarjeta "Sobre máximo"
  - Removidas referencias a ALERT_SOBRE_MAXIMO

- `src/sisalmacen/ui/pages/products_page.py`
  - Removidas referencias a ALERT_SOBRE_MAXIMO
  - Removidos colores de fila para sobre máximo

- `src/sisalmacen/ui/dialogs/product_dialog.py`
  - Removido campo de entrada para stock_maximo

#### Test Layer
- `tests/integration/test_inventory_flow.py`
  - Removida prueba: `test_compute_alert_respects_max_setting()`
  - Actualizada: `test_alerts_and_dashboard()` (solo AGOTADO y BAJO_MINIMO)

- `tests/unit/test_domain_rules.py`
  - Actualizada: Parametrized test para `compute_alert()` (sin parámetro maximum)

---

## Prioridad 2: Normalizar Alertas ?

### Justificación
La nomenclatura fue inconsistente: código usaba `ALERT_SIN_STOCK` pero especificación requería `AGOTADO`. Se normaliza a través de todo el sistema.

### Cambios Realizados (7 archivos)

| Archivo | Cambio |
|---------|--------|
| `src/sisalmacen/domain/inventory.py` | `ALERT_SIN_STOCK` ? `ALERT_AGOTADO`; label: "Agotado" |
| `src/sisalmacen/infrastructure/db/catalog_product_repositories.py` | `ALERT_SIN_STOCK` ? `ALERT_AGOTADO` en condiciones |
| `src/sisalmacen/ui/pages/dashboard_page.py` | Tarjeta de alerta renombrada "Agotados" |
| `src/sisalmacen/ui/pages/products_page.py` | Color de fila y filtro actualizados |
| `src/sisalmacen/application/reports.py` | Labels y cálculos de alerta actualizados |
| `tests/integration/test_inventory_flow.py` | Aserciones actualizadas: AGOTADO |
| `tests/unit/test_domain_rules.py` | Test cases actualizados |

### Resultado
Alertas disponibles (3 estados):
- `ALERT_AGOTADO` = "Agotado" (stock = 0)
- `ALERT_BAJO_MINIMO` = "Bajo mínimo" (0 < stock < stock_minimo)
- `ALERT_CUALQUIERA` = Filtro: cualquiera de las dos

---

## Prioridad 3: Infraestructura CSV ?

### Nuevo Archivo Creado

#### `src/sisalmacen/application/csv_export.py`
Módulo utilitario de exportación CSV con:

**Función principal:**
```python
export_to_csv(headers: Sequence[str], rows: Sequence[dict], *, has_bom=True) -> str
```
- Genera CSV con UTF-8 BOM (compatible con Excel)
- Convierte tipos: Decimal ? str, bool ? "ACTIVO"/"INACTIVO", date ? ISO
- Maneja encabezados dinámicos

**Constantes de cabeceras:**
```python
PRODUCTOS_CSV_HEADERS = [
    "codigo_producto", "descripcion", "descripcion_adicional", "marca", 
    "categoria", "precio_compra", "precio_venta", "stock_minimo", 
    "stock_inicial", "entradas", "salidas", "stock_actual", "almacen", 
    "ubicacion", "proveedor", "fecha_registro", "estado", "observacion"
]

MOVIMIENTOS_CSV_HEADERS = [
    "tipo_movimiento", "fecha", "codigo_producto", "descripcion", 
    "cantidad", "um", "documento", "almacen", "ubicacion", 
    "proveedor", "observacion"
]
```

### Métodos Agregados a Servicios

#### ProductService
```python
def get_csv_template(self) -> str
    # Retorna plantilla CSV vacía

def export_csv(product_filter: ProductFilter, page: int = 1) -> str
    # Exporta productos filtrados a CSV

def import_csv(csv_content: str) -> dict[str, int]
    # Importa productos desde CSV
    # Retorna: {"created": int, "errors": int}
```

#### MovementService
```python
def get_csv_template(self) -> str
    # Retorna plantilla CSV vacía para movimientos

def export_csv(movement_filter: MovementFilter) -> str
    # Exporta movimientos filtrados a CSV

def import_csv(csv_content: str) -> dict[str, int]
    # Importa movimientos desde CSV
    # Retorna: {"created": int, "errors": int}
```

### Características
- ? UTF-8 BOM para compatibilidad con Excel
- ? Conversión automática de tipos
- ? Encabezados configurables
- ? Soporte para productos y movimientos

---

## Prioridad 4: UI Buttons e Importación ?

### Archivos Modificados (2 páginas)

#### ProductsPage (`src/sisalmacen/ui/pages/products_page.py`)

**Botones agregados** (después de "Nuevo producto"):
- "Importar CSV" (permiso: `productos.crear`)
- "Descargar plantilla" (permiso: `productos.ver`)

**Métodos implementados:**
```python
def _import_csv(self) -> None
    # 1. Abre QFileDialog para seleccionar CSV
    # 2. Lee contenido del archivo
    # 3. Muestra CSVImportDialog con preview
    # 4. Llamar a ProductService.import_csv()
    # 5. Muestra resultado (creados/errores)

def _download_template(self) -> None
    # 1. Abre QFileDialog para guardar
    # 2. Descarga plantilla via ProductService.get_csv_template()
    # 3. Guarda archivo
```

#### MovementsPage (`src/sisalmacen/ui/pages/movements_page.py`)

**Botones agregados** (después de "Ajustar inventario"):
- "Importar CSV" (permiso: `movimientos.entrada`)
- "Descargar plantilla" (permiso: `movimientos.ver`)

**Métodos implementados:**
- Idénticos a ProductsPage pero usan MovementService

### Nuevo Diálogo Creado

#### `src/sisalmacen/ui/dialogs/csv_import_dialog.py`

**CSVImportDialog**
- Muestra preview de registros a importar
- Tabla con datos del CSV parseados
- Botones OK/Cancel
- Maneja BOM UTF-8 automáticamente

**Uso:**
```python
dialog = CSVImportDialog(csv_content, headers, parent=self)
if dialog.exec() == QDialog.DialogCode.Accepted:
    rows = dialog.get_rows()
    # Procesar importación
```

---

## Flujo Completo (MVP)

### Exportación
1. Usuario abre Productos o Movimientos
2. Hace clic en "Descargar plantilla"
3. Selecciona ubicación para guardar ? OK
4. Archivo CSV se descarga con:
   - Encabezados correctos
   - Una fila de ejemplo (vacía)
   - UTF-8 con BOM

### Importación
1. Usuario hace clic en "Importar CSV"
2. Selecciona archivo CSV ? Aceptar
3. Sistema lee y parsea el CSV
4. Se muestra CSVImportDialog con preview
5. Usuario revisa registros a importar ? OK
6. Sistema ejecuta:
   - Valida filas individuales
   - Crea registros exitosos
   - Cuenta errores
7. Se muestra resumen: "Creados: X, Errores: Y"
8. Página se actualiza mostrando nuevos datos

---

## Validación y Errores Manejados

### Importación de Productos
- ? Campos obligatorios: codigo_producto, descripcion
- ? Stock mínimo se convierte a int
- ? Errores por fila se cuentan sin detener importación
- ? Resultado sumario (creados/errores)

### Importación de Movimientos
- ? Campos obligatorios: codigo_producto, tipo_movimiento
- ? Tipo debe ser: ENTRADA o SALIDA
- ? Cantidad se convierte a int
- ? Fecha se intenta parsear (fallback a hoy)
- ? Resultado sumario

---

## Limitaciones Actuales (Para Mejora Futura)

1. **Validación**
   - No valida existencia de categorías/marcas
   - No verifica rango de valores
   - No detecta duplicados

2. **Campos No Soportados**
   - Productos: no importa marca, categoria, proveedor, precios
   - Movimientos: no importa documento, almacen, ubicacion, observacion

3. **Features Avanzadas No Implementadas**
   - No auto-detecta codificación/separador
   - No exporta informe de errores
   - No muestra barra de progreso
   - No detecta reimportaciones
   - No aplica stock (modo "Aplicar stock" de especificación)

---

## Verificación de Cambios

### Sin Errores de Compilación
- ? `products_page.py` - OK
- ? `movements_page.py` - OK
- ? `csv_import_dialog.py` - OK
- ? `products.py` (service) - OK
- ? `movements.py` (service) - OK

### Integridad del Código
- ? Sin referencias huérfanas a `stock_maximo`
- ? Nomenclatura consistente: `ALERT_AGOTADO`
- ? Imports correctos en todos los archivos
- ? Métodos de servicio accesibles desde UI

---

## Documentación Relacionada

- [04_Decisiones_Arquitectura_y_Reglas.md](04_Decisiones_Arquitectura_y_Reglas.md) — Decisiones técnicas
- [06_Especificacion_CSV.md](06_Especificacion_CSV.md) — Especificación CSV completa
- [07_Permisos_CasosUso_Pantallas.md](07_Permisos_CasosUso_Pantallas.md) — Permisos aplicados
- [08_Backlog_y_Plan_de_Pruebas.md](08_Backlog_y_Plan_de_Pruebas.md) — Plan general

---

## Próximos Pasos Recomendados

1. **Testing**
   - Ejecutar `pytest` para verificar suite de tests
   - UAT manual: crear/importar/exportar datos

2. **Mejoras Propuestas (Prioridad)**
   - Alta: Validación más robusta de campos CSV
   - Media: Soporte de más campos en importación
   - Media: Audit logging para imports
   - Baja: Progress bar, exportar errores, detección de duplicados

3. **Empaquetado**
   - Actualizar `SisAlmacenInstaller.iss` si es necesario
   - Generar build de prueba con PyInstaller

---

**Fecha de implementación:** 2025
**Estado:** MVP completo - Listo para UAT básico
