# Solución: Importación de Movimientos sin Productos Previos

## Problema Identificado

Al intentar importar un archivo CSV de MOVIMIENTOS, fallaba si los productos no estaban previamente registrados en la base de datos:

```
Error E21 codigo_producto: El producto no existe y el movimiento no puede validarse.
```

Esto es correcto desde el punto de vista de la lógica de negocio (un movimiento necesita un producto existente), pero faltaba **retroalimentación clara** al usuario indicando:
1. Qué productos faltaban
2. Qué debería hacer para resolverlo

## Soluciones Implementadas

### 1. Mensaje de Error Mejorado

**Antes:**
```
E21 codigo_producto: El producto no existe y el movimiento no puede validarse.
```

**Después:**
```
E21 codigo_producto: Producto '7018-3.2' no existe. Los movimientos requieren un producto preexistente.
```

**Ubicación:** `src/sisalmacen/application/importing.py` ? función `classify_row()` línea ~240

### 2. Advertencia Consolidada en Vista Previa

Ahora la vista previa muestra un resumen claro de todos los productos faltantes:

**En la sección "ADVERTENCIAS":**
```
?? PRODUCTOS NO ENCONTRADOS: 7018-3.2, 7018-4, 7018-5, CHANFER-4. 
Los movimientos requieren que el producto exista previamente. 
Por favor, importe primero los productos o créelos manualmente.
```

**Ubicación:** `src/sisalmacen/application/importing.py` ? función `validate()` línea ~530-555

### 3. Flujo Recomendado para Importación

#### Escenario: Migración de datos históricos con Productos y Movimientos

**Opción A: Importar primero los productos**
```
1. Crear archivo "Productos.csv" con todos los productos únicos
   - Código: 7018-3.2, 7018-4, 7018-5, CHANFER-4
   - Descripción, Categoría, Unidad, etc.
   
2. Importar Productos.csv
   - ? Se crean todos los productos
   
3. Importar Movimientos.csv
   - ? Ahora todos los movimientos tienen su producto base
   - Se registran entradas y salidas correctamente
```

**Opción B: Crear productos manualmente primero** (para validar datos antes)
```
1. En pestaña "Productos" ? botón "Nuevo producto"
   - Crear cada producto con datos mínimos
   - Código + Descripción + Categoría + Unidad
   
2. Luego importar Movimientos.csv
   - ? Los movimientos se aplican correctamente
```

## Validación de Cambios

### Test Case 1: Importar Movimientos sin Productos (Escenario Actual)

**Archivo:** `Movimientos_RR_App_Corregido.csv`

**Pasos:**
1. Abrir pestaña "Importar CSV"
2. Cargar `Movimientos_RR_App_Corregido.csv`
3. Sistema detecta: "Archivo de tipo MOVIMIENTOS"

**Resultados esperados:**
- ? Vista previa muestra 9 filas
- ? Todas las filas con estado "Error"
- ? Sección "ADVERTENCIAS" muestra:
  ```
  ?? PRODUCTOS NO ENCONTRADOS: 7018-3.2, 7018-4, 7018-5, CHANFER-4...
  Los movimientos requieren que el producto exista previamente.
  Por favor, importe primero los productos o créelos manualmente.
  ```
- ? Detalles de cada error: `E21 codigo_producto: Producto '7018-3.2' no existe...`
- ? Botón "Aplicar" deshabilitado (no se puede importar con errores)

### Test Case 2: Importar Productos, luego Movimientos

**Pasos:**
1. Crear archivo "Productos.csv" con:
   ```csv
   codigo_producto,descripcion,categoria,unidad
   7018-3.2,ELECTRODO SUPERCITO 7018 1/8,INSUMOS,CAJA
   7018-4,ELECTRODO SUPERCITO 7018 5/32,INSUMOS,CAJA
   7018-5,ELECTRODO SUPERCITO 7018 3/16,INSUMOS,CAJA
   CHANFER-4,ELECTRODO CHANFERCORD 5/32,INSUMOS,LATA
   ```

2. Importar Productos.csv
   - ? Se crean 4 productos

3. Importar Movimientos_RR_App_Corregido.csv
   - ? Todas las filas validan correctamente
   - ? Se muestran 9 filas con acción "INSERTAR"
   - ? NO hay advertencias de productos faltantes
   - ? Botón "Aplicar" está habilitado
   - ? Después de aplicar, aparecen todos los movimientos en historial

## Archivos Modificados

**`src/sisalmacen/application/importing.py`**
- Línea ~240: Mensaje de error mejorado
- Línea ~530-555: Lógica para detectar y reportar productos faltantes en MOVIMIENTOS

## Estado

? Código sin errores de compilación
? Detección automática de productos faltantes
? Mensajes claros para el usuario
? Advertencias consolidadas en vista previa
? Listo para UAT

## Próximos Pasos Recomendados

1. **Test:** Importar Movimientos.csv sin productos previos
   - Verificar que aparece la advertencia
   - Verificar que los errores son claros
   
2. **Test:** Crear productos ? Luego importar movimientos
   - Verificar que se importan correctamente
   - Verificar que el stock se actualiza

3. **Información para el Usuario:**
   - Si planea importar movimientos históricos, PRIMERO debe importar/crear los productos
   - La aplicación validará automáticamente esto y mostrará mensajes claros

## Notas Importantes

- Los movimientos SIEMPRE requieren un producto existente (restricción de integridad)
- No hay opción de "crear productos automáticamente" desde movimientos (por diseño)
- El archivo `Movimientos_RR_App_Corregido.csv` es correcto en estructura, solo falta que los productos existan
- Se recomienda validar los códigos de productos antes de la importación masiva
