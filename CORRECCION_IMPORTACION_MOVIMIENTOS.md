# Corrección: Importación de Movimientos CSV - Error "Faltan columnas obligatorias: categoria"

## Problema Identificado

El archivo CSV de Movimientos fallaba con error:
```
Faltan columnas obligatorias: categoria
```

Aunque el archivo tenía todos los campos requeridos (`tipo_movimiento`, `fecha`, `codigo_producto`, `cantidad`, `um`), el sistema estaba validando como si fuera un archivo de Productos.

### Causa Raíz

El método `validate()` en `ImportService` no estaba detectando el tipo de archivo (Productos vs Movimientos) y usaba siempre `REQUIRED_FOR_INSERT` que es específica de Productos:

```python
# ANTES (incorrecto):
required = ("codigo",) if options.mode == "ACTUALIZAR" else REQUIRED_FOR_INSERT
# REQUIRED_FOR_INSERT = ("codigo_producto", "descripcion")
# Pero para Movimientos necesitaba: ("tipo_movimiento", "fecha", "codigo_producto", "cantidad", "um")
```

## Soluciones Implementadas

### 1. **Actualización de Imports** (`application/importing.py`)
Agregó importación de tipos y funciones para detección de archivo:
- `COLUMNS_PRODUCTOS`, `COLUMNS_MOVIMIENTOS`
- `REQUIRED_FOR_MOVEMENT`
- `FileType`, `detect_file_type()`

### 2. **Ampliación de _HEADER_ALIASES** (`application/importing.py`)
Agregó mapping para campos de MOVIMIENTOS:
```python
"tipo_movimiento": ("tipo_movimiento",),
"fecha": ("fecha",),
"codigo_producto": ("codigo_producto",),
"cantidad": ("cantidad",),
"um": ("um", "unidad_medida"),
"documento": ("documento",),
"almacen": ("almacen",),
"observacion": ("observacion", "observaciones"),
```

### 3. **Actualización de resolve_headers()** (`application/importing.py`)
Ahora detecta el tipo de archivo:
```python
# ANTES:
def resolve_headers(headers: list[str]) -> tuple[dict[str, str], list[str], bool]:

# DESPUÉS:
def resolve_headers(headers: list[str]) -> tuple[dict[str, str], list[str], bool, FileType]:
    # ... validación ...
    file_type = detect_file_type(headers)  # ? NUEVO
    return resolved, warnings, legacy_product_format, file_type
```

### 4. **Refactorización de validate()** (`application/importing.py`)
Ahora selecciona validadores según tipo:
```python
header_map, warnings, legacy_product_format, file_type = resolve_headers(content.headers)

# Determinar campos requeridos según el tipo de archivo detectado
if file_type == FileType.MOVIMIENTOS:
    required = REQUIRED_FOR_MOVEMENT
    columns_to_use = COLUMNS_MOVIMIENTOS
elif file_type == FileType.PRODUCTOS:
    required = ("codigo",) if options.mode == "ACTUALIZAR" else REQUIRED_FOR_INSERT
    columns_to_use = COLUMNS_PRODUCTOS
else:
    # Fallback a Productos para compatibilidad retroactiva
    required = ("codigo",) if options.mode == "ACTUALIZAR" else REQUIRED_FOR_INSERT
    columns_to_use = COLUMNS_PRODUCTOS

# Actualizar file_type en las opciones
options = ImportOptions(
    # ... parámetros anteriores ...
    file_type=file_type,  # ? NUEVO: Pasar tipo detectado
)
```

## Flujo de Validación Mejorado

```
Archivo CSV cargado
    ?
resolve_headers()
    ? (detecta automáticamente)
FileType.MOVIMIENTOS
    ?
REQUIRED_FOR_MOVEMENT = ("tipo_movimiento", "fecha", "codigo_producto", "cantidad", "um")
COLUMNS_MOVIMIENTOS = (11 campos específicos)
    ?
? Validación correcta
```

## Cambios en Comportamiento

| Escenario | Antes | Después |
|-----------|-------|---------|
| CSV con `tipo_movimiento` | ? Error "categoria" | ? Detecta MOVIMIENTOS, valida correctamente |
| CSV con `codigo_producto` + `descripcion` | ? Valida como PRODUCTOS | ? Detecta PRODUCTOS, valida correctamente |
| CSV antiguo con `codigo` + `nombre` | ? Valida como PRODUCTOS | ? Fallback a PRODUCTOS, valida correctamente |

## Testing

### Caso 1: Importar Movimientos_RR_App.csv
```csv
tipo_movimiento,fecha,codigo_producto,descripcion,cantidad,um,...
ENT,2023-11-01,7018-3.2,ELECTRODO,25,CAJA,...
```
**Esperado:** ? Validación exitosa (campos movimientos correctos)

### Caso 2: Importar Productos_RR_App.csv
```csv
codigo_producto,descripcion,marca,categoria,...
7018-3.2,ELECTRODO SUPERCITO,...
```
**Esperado:** ? Validación exitosa (campos productos correctos)

### Caso 3: Archivo sin tipo definible
```csv
codigo,nombre,categoria,...
```
**Esperado:** ? Fallback a PRODUCTOS (compatibilidad retroactiva)

## Archivos Modificados

1. `src/sisalmacen/application/importing.py`
   - Imports actualizados
   - _HEADER_ALIASES expandido
   - resolve_headers() con detección de tipo
   - validate() con lógica de detección

2. `src/sisalmacen/domain/importing.py` (sin cambios en esta sesión)
   - Ya contenía FileType, detect_file_type(), COLUMNS_MOVIMIENTOS, REQUIRED_FOR_MOVEMENT

## Status

? Código compila sin errores
? Lógica de detección integrada
? Fallback a compatibilidad retroactiva
? Listo para UAT

## Próximos Pasos

1. Probar importación de `Movimientos_RR_App.csv`
2. Verificar que se muestra vista previa correcta (sin mensaje de error)
3. Probar importación de `Productos_RR_App.csv` (debe seguir funcionando)
4. Revisar alertas de stock mínimo (segundo problema del usuario)
