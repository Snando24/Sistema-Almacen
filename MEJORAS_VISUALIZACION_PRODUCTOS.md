# Mejoras en Visualización de Productos y Alertas de Stock Mínimo

## Cambios Implementados

### 1. **Tabla de Productos Simplificada** ?

**Archivo:** `src/sisalmacen/ui/pages/products_page.py`

**Cambio:** Reducción de columnas mostradas en la tabla principal

**Antes:**
- Código
- Descripción
- Categoría
- Unidad
- Stock
- Mínimo
- Precio venta (si tiene permisos)
- Estado
- Alerta

**Después:**
- Código
- Descripción
- Stock
- Mínimo
- Estado
- Alerta

**Justificación:** 
- La tabla ahora es más compacta y legible
- Enfatiza información esencial: stock actual vs mínimo + alertas
- Categoría, Unidad, Precio y otros detalles están disponibles en "Detalle e historial"

**Detalle del Producto** (Modal de detalle disponible con clic en "Detalle e historial"):
- Código
- Descripción principal
- Estado
- Categoría
- Unidad
- Código de barras
- Marca
- Proveedor
- Ubicación
- Stock actual
- Stock mínimo
- Alerta
- Precio compra / venta
- Registrado
- Actualizado
- **Historial de movimientos** (últimos 200 registros)

### 2. **Alertas de Stock Bajo Mínimo Mejoradas** ?

**Archivo:** `src/sisalmacen/ui/dialogs/product_dialog.py`

**Cambio:** Mostrar alerta cuando el producto esté bajo stock mínimo después de guardar

**Comportamiento:**
1. Usuario abre diálogo de editar producto
2. Modifica el stock mínimo o cantidad
3. Guarda los cambios
4. Sistema verifica automáticamente si stock ? stock_minimo
5. Si está bajo mínimo, muestra cuadro de diálogo de advertencia con:
   - Código del producto
   - Stock actual
   - Stock mínimo
   - Mensaje claro "Este producto está por debajo del stock mínimo configurado"

**Ejemplo:**
```
?? Stock bajo mínimo
????????????????????
Producto: 7018-3.2
Stock actual: 11
Stock mínimo: 12

Este producto está por debajo del stock mínimo configurado.
```

**Nota Técnica:**
- La lógica de cálculo de alerta ya estaba correcta en `domain/inventory.py` ? función `compute_alert()`
- La fórmula es: `cantidad <= stock_minimo` ? ALERT_BAJO_MINIMO
- El problema era que no había feedback visual al usuario cuando guardaba un producto que pasaba a estar bajo mínimo

### 3. **Flujo de Actualización de Tabla**

**Archivo:** `src/sisalmacen/ui/pages/products_page.py`

**Confirmación:** El flujo ya estaba correctamente implementado:
1. Usuario hace clic en "Editar"
2. Se abre ProductDialog
3. Usuario guarda cambios
4. Diálogo se cierra (accept())
5. Se llama automáticamente a `self.refresh()` en products_page.py
6. Tabla se recarga con los datos actualizados incluyendo la nueva alerta

## Validación de Cambios

### Caso de Prueba 1: Stock Bajo Mínimo
```
1. Crear producto: Código=TEST-001, Stock=11, Mínimo=12
2. Guardar
3. Resultado esperado: ?? Alerta "Stock bajo mínimo" aparece
4. Tabla muestra: Alerta=BAJO_MINIMO (celda con fondo amarillo)
```

### Caso de Prueba 2: Actualización Dinámica de Alerta
```
1. Abrir producto con Stock=5, Mínimo=3 (sin alerta)
2. Cambiar Mínimo a 6
3. Guardar
4. Resultado esperado: ?? Alerta "Stock bajo mínimo" aparece
5. Tabla se actualiza y muestra nueva alerta
```

### Caso de Prueba 3: Producto Agotado
```
1. Abrir producto con Stock=0
2. Cualquier cambio
3. Guardar
4. Resultado esperado: ?? Alerta "Stock Agotado" (diferente a bajo mínimo)
```

## Archivos Modificados

1. `src/sisalmacen/ui/pages/products_page.py`
   - Línea ~115-124: Reducción de columnas en headers
   - Línea ~245-260: Simplificación de construcción de filas

2. `src/sisalmacen/ui/dialogs/product_dialog.py`
   - Línea ~14: Import de ALERT_BAJO_MINIMO
   - Línea ~170-210: Mejora de _save() con verificación de alerta

## Estado Actual

? Código sin errores de compilación
? Tabla de productos muestra solo columnas esenciales
? Alerta de stock bajo mínimo funciona después de guardar
? Tabla se actualiza correctamente después de editar
? Detalle del producto sigue disponible con toda la información
? Compatible con sistema de permisos existente

## Próximos Pasos (Opcional)

1. **Dashboard de Alertas:** Mostrar en el dashboard solo productos con alertas
2. **Notificaciones:** Sistema de notificaciones para stock bajo mínimo
3. **Importación:** Mostrar alertas durante importación de CSV si hay productos bajo mínimo
4. **Reportes:** Generar reporte de productos bajo mínimo para revisión

## Notas Importantes

- La lógica de alertas está centralizada en `domain/inventory.py::compute_alert()`
- La tabla ahora se enfoca en lo esencial, minimizando distracciones
- El detalle del producto sigue siendo la fuente de información completa
- Las alertas se calculan dinámicamente basadas en stock actual y mínimo configurado
