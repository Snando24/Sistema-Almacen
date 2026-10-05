# Detección de Tipo de Importación: Productos vs Movimientos

## Problema Resuelto

El sistema anteriormente trataba todos los CSVs de forma genérica, mostrando opciones que no aplicaban a ambos tipos:
- Archivos de **Productos** mostraban opciones correctas
- Archivos de **Movimientos** mostraban opciones inapropiadas (apply_stock, create_missing_catalogs)
- No había forma de detectar automáticamente el tipo de CSV

## Solución Implementada

### 1. **Domain Layer** (`src/sisalmacen/domain/importing.py`)

#### Agregado: Enum `FileType`
```python
class FileType(Enum):
    PRODUCTOS = "productos"
    MOVIMIENTOS = "movimientos"
    DESCONOCIDO = "desconocido"
```

#### Agregado: Función `detect_file_type()`
Analiza los headers del CSV para determinar el tipo:
- Si contiene `tipo_movimiento` ? **MOVIMIENTOS**
- Si contiene `codigo_producto` Y `descripcion` ? **PRODUCTOS**
- Si no coincide ? **DESCONOCIDO** (compatibilidad retroactiva)

#### Actualizado: `ImportOptions`
Agregó campo `file_type: FileType = FileType.DESCONOCIDO` para almacenar el tipo detectado.

### 2. **Application Layer** (`src/sisalmacen/application/importing.py`)

#### Modificado: Función `validate()`
1. **Detecta el tipo** usando `detect_file_type()` con los headers del archivo
2. **Selecciona campos requeridos** según el tipo:
   - **PRODUCTOS**: `REQUIRED_FOR_INSERT` (codigo_producto, descripcion)
   - **MOVIMIENTOS**: `REQUIRED_FOR_MOVEMENT` (tipo_movimiento, fecha, codigo_producto, cantidad, um)
3. **Selecciona columnas** según el tipo:
   - **PRODUCTOS**: `COLUMNS_PRODUCTOS` (18 campos)
   - **MOVIMIENTOS**: `COLUMNS_MOVIMIENTOS` (11 campos)
4. **Pasa el tipo** en las opciones al procesar filas para validación tipo-específica

### 3. **UI Layer** (`src/sisalmacen/ui/pages/import_page.py`)

#### Agregado: Campo `_detected_file_type`
Almacena el tipo de archivo detectado para uso en la UI.

#### Agregado: Función `_detect_file_type(file_path)`
Cuando el usuario selecciona un archivo:
1. Lee solo el encabezado (primera línea) para eficiencia
2. Detecta el separador automáticamente (`,` `;` o `\t`)
3. Llama a `detect_file_type()` para determinar si es Productos o Movimientos

#### Agregado: Función `_update_options_visibility()`
Actualiza la visibilidad de controles según el tipo detectado:
- **Para MOVIMIENTOS**: Oculta `create_missing_catalogs` y `apply_stock`
- **Para PRODUCTOS**: Muestra ambas opciones (respetando permisos)
- **Para DESCONOCIDO**: Muestra todas las opciones (compatibilidad)

#### Modificado: Función `_browse()`
Ahora llama a `_detect_file_type()` y `_update_options_visibility()` cuando se selecciona archivo.

#### Modificado: Función `_read_options()`
Incluye `file_type=self._detected_file_type` en las opciones retornadas.

## Flujo de Detección

```
Usuario selecciona archivo (Browse)
        ?
_browse() ejecuta:
  1. _detect_file_type(path) 
     ? Lee headers del CSV
     ? Llama detect_file_type()
     ? Almacena resultado en self._detected_file_type
  2. _update_options_visibility()
     ? Muestra/oculta controles según tipo
  3. _update_buttons()
     ? Actualiza estado UI
        ?
Usuario hace clic en "Validar archivo"
        ?
validate() ejecuta:
  1. Lee archivo completamente con reader
  2. Detecta tipo usando detect_file_type(headers)
  3. Selecciona validadores según tipo
  4. Pasa file_type en ImportOptions
        ?
Resultado: Validación tipo-específica correcta
```

## Ejemplos de Detección

### Archivo de Productos
Headers: `codigo_producto, descripcion, marca, categoria, ...`
? Detecta: `FileType.PRODUCTOS`
? Muestra: `create_missing_catalogs`, `apply_stock`
? Valida con: `COLUMNS_PRODUCTOS`, `REQUIRED_FOR_INSERT`

### Archivo de Movimientos  
Headers: `tipo_movimiento, fecha, codigo_producto, cantidad, um, ...`
? Detecta: `FileType.MOVIMIENTOS`
? Oculta: `create_missing_catalogs`, `apply_stock`
? Valida con: `COLUMNS_MOVIMIENTOS`, `REQUIRED_FOR_MOVEMENT`

### Archivo Antiguo (compatibilidad)
Headers: `codigo, nombre, categoria, unidad, ...`
? Detecta: `FileType.DESCONOCIDO`
? Muestra: Todas las opciones
? Valida como: `COLUMNS_PRODUCTOS` (compatibilidad retroactiva)

## Cambios de Comportamiento

| Aspecto | Antes | Después |
|---------|-------|---------|
| Detección de tipo | Manual o por nombre | Automática por headers |
| Opciones UI | Siempre las mismas | Dinámicas según tipo |
| Validación | Genérica | Tipo-específica |
| Campos requeridos | Fijos | Dependen del tipo |
| Columnas procesadas | 18 (PRODUCTOS) | 18 o 11 según tipo |

## Beneficios

? **Experiencia de usuario mejorada**: Opciones relevantes según tipo de archivo  
? **Prevención de errores**: No se puede usar opciones inapropiadas  
? **Validación correcta**: Cada tipo valida con sus reglas específicas  
? **Compatibilidad**: Archivos antiguos siguen funcionando  
? **Automatización**: Detección sin intervención del usuario  

## Archivos Modificados

1. `src/sisalmacen/domain/importing.py` - Definiciones de tipos y detección
2. `src/sisalmacen/application/importing.py` - Validación tipo-específica
3. `src/sisalmacen/ui/pages/import_page.py` - UI con opciones dinámicas

## Testing Recomendado

1. Importar `Productos_RR_App.csv` ? Debe detectar PRODUCTOS, mostrar todas las opciones
2. Importar `Movimientos_RR_App.csv` ? Debe detectar MOVIMIENTOS, ocultar apply_stock
3. Importar archivo antiguo ? Debe detectar DESCONOCIDO, mostrar todas las opciones
4. Validar que `create_missing_catalogs` NO afecta a importaciones de Movimientos
5. Validar que `apply_stock` NO afecta a importaciones de Movimientos
