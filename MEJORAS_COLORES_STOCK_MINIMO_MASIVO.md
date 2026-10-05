# Mejoras Visuales y Stock Mínimo Masivo

## 1. Colores Adaptativos para Modo Oscuro ?

### Problema
Los colores de alerta en la tabla de productos eran demasiado claros en modo oscuro:
- **AGOTADO**: `#fde2e4` (rojo muy claro - apenas visible en fondo oscuro)
- **BAJO_MINIMO**: `#fff3cd` (amarillo muy claro - difícil de leer en oscuro)
- **Inactivo**: `#e5e5e2` (gris claro - bajo contraste en oscuro)

### Solución Implementada

**Archivo:** `src/sisalmacen/ui/pages/products_page.py`

**Cambios:**
1. Importar `current_theme_mode()` y `THEME_DARK` de `theme.py`
2. Crear funciones dinámicas que devuelven colores según el tema actual:
   ```python
   def _get_alert_colors() -> dict[str, QColor]:
       """Devuelve colores de alerta adaptados al tema actual (claro/oscuro)."""
       is_dark = current_theme_mode() == THEME_DARK
       return {
           ALERT_AGOTADO: QColor("#7f1d1a") if is_dark else QColor("#fde2e4"),
           ALERT_BAJO_MINIMO: QColor("#713f12") if is_dark else QColor("#fff3cd"),
       }
   
   def _get_inactive_color() -> QColor:
       """Devuelve el color para productos inactivos adaptado al tema actual."""
       is_dark = current_theme_mode() == THEME_DARK
       return QColor("#3a4248") if is_dark else QColor("#e5e5e2")
   ```

3. Actualizar `refresh()` para recalcular colores dinámicamente:
   ```python
   # Recalcular colores según el tema actual
   alert_colors = _get_alert_colors()
   inactive_color = _get_inactive_color()
   ```

### Colores Usados

#### Modo Claro (THEME_LIGHT)
- AGOTADO: `#fde2e4` (rojo pastel)
- BAJO_MINIMO: `#fff3cd` (amarillo pastel)
- Inactivo: `#e5e5e2` (gris claro)

#### Modo Oscuro (THEME_DARK)
- AGOTADO: `#7f1d1a` (rojo oscuro con buena legibilidad)
- BAJO_MINIMO: `#713f12` (naranja-marrón oscuro)
- Inactivo: `#3a4248` (gris oscuro)

### Resultado
? Los colores se adaptan automáticamente al cambiar entre modo claro y oscuro
? Mejor contraste en ambos modos
? Las alertas son claramente visibles sin importar el tema

---

## 2. Stock Mínimo Global/Masivo ?

### Características

**Archivo:** `src/sisalmacen/ui/pages/products_page.py`

**Nuevos componentes:**

1. **Botón "Establecer stock mínimo"**
   - Ubicado en la barra de acciones después de "Descargar plantilla"
   - Habilitado solo si el usuario tiene permiso `productos.editar`
   - Abre un diálogo de configuración

2. **Diálogo `BulkMinimumDialog`**
   - Campo de entrada para el valor de stock mínimo
   - Validación de entrada (número decimal)
   - Confirmación antes de aplicar
   - Información clara sobre el alcance de la acción

### Flujo de Uso

```
1. Usuario hace clic en "Establecer stock mínimo"
   ?
2. Se abre diálogo BulkMinimumDialog
   - Etiqueta: "Stock mínimo para TODOS los productos"
   - Información: "Esta acción establecerá el stock mínimo indicado para TODOS los productos activos."
   ?
3. Usuario ingresa valor (ej: 10)
   ?
4. Usuario hace clic en "Aplicar"
   ?
5. Sistema pide confirmación:
   "¿Establecer el stock mínimo en 10 para TODOS los productos activos?
    Esta acción no se puede deshacer."
   ?
6. Si confirma:
   - Se obtienen todos los productos ACTIVOS
   - Se actualiza stock_minimo para cada uno
   - Muestra confirmación: "Se actualizó el stock mínimo para X producto(s)."
   ?
7. Tabla se recarga automáticamente con las nuevas alertas
```

### Seguridades Implementadas

? **Confirmación de usuario** - Pide confirmación antes de aplicar
? **Solo productos activos** - Nunca modifica productos inactivos
? **Validación de entrada** - Verifica que sea un número válido
? **Permisos** - Solo disponible si `productos.editar` está habilitado
? **Transparencia** - Muestra claramente cuántos productos fueron actualizados

### Ejemplo de Uso

**Escenario:** Se necesita establecer stock mínimo de 25 cajas para todos los productos

```
1. Barra de acciones ? Botón "Establecer stock mínimo"
2. Se abre diálogo
3. Ingresar: 25
4. Clic en "Aplicar"
5. Confirmación: "¿Establecer el stock mínimo en 25 para TODOS los productos activos?"
6. Clic en "Ok"
7. Resultado: "Se actualizó el stock mínimo para 230 producto(s)."
8. Tabla se actualiza mostrando las nuevas alertas
```

---

## Archivos Modificados

| Archivo | Cambios |
|---------|---------|
| `src/sisalmacen/ui/pages/products_page.py` | <ul><li>Imports de theme y ProductData</li><li>Funciones `_get_alert_colors()` y `_get_inactive_color()`</li><li>Método `refresh()` actualizado para colores dinámicos</li><li>Botón "Establecer stock mínimo" agregado</li><li>Método `_set_bulk_minimum()` agregado</li><li>Clase `BulkMinimumDialog` nueva</li></ul> |

---

## Validación de Cambios

### Test Case 1: Colores en Modo Oscuro
1. Cambiar aplicación a "Modo oscuro"
2. Abrir pestaña Productos
3. **Esperado:** Alertas (rojo/naranja oscuro) claramente visibles
4. **Esperado:** Productos inactivos (gris oscuro) legibles

### Test Case 2: Colores en Modo Claro
1. Cambiar aplicación a "Modo claro"
2. Abrir pestaña Productos
3. **Esperado:** Alertas (rojo/amarillo pastel) visibles
4. **Esperado:** Productos inactivos (gris claro) legibles

### Test Case 3: Stock Mínimo Global
1. Tener al menos 5 productos activos sin stock mínimo
2. Botón "Establecer stock mínimo" ? Clic
3. Ingresar valor: `15`
4. Clic "Aplicar"
5. Confirmación aparece ? Clic "Ok"
6. **Esperado:** Mensaje "Se actualizó el stock mínimo para X producto(s)."
7. **Esperado:** Tabla se recarga
8. **Esperado:** Productos con stock < 15 muestran alerta "BAJO_MINIMO"

### Test Case 4: Productos Inactivos No Afectados
1. Crear producto inactivo con stock_minimo = NULL
2. Ejecutar "Establecer stock mínimo" con valor 20
3. **Esperado:** Producto inactivo NO es modificado
4. **Verificar:** Abrir detalle del producto inactivo
5. **Esperado:** Stock mínimo sigue siendo NULL/vacío

---

## Notas Importantes

- Los colores se recalculan en cada `refresh()`, garantizando adaptación al cambio de tema
- La operación masiva es **IRREVERSIBLE** - no hay deshacer directo
- Se recomienda hacer un backup antes de operaciones masivas
- El diálogo muestra información clara sobre qué se va a hacer
- Solo se actualizan productos ACTIVOS (por diseño)

---

## Status

? Código sin errores de compilación
? Colores dinámicos implementados
? Stock mínimo masivo implementado
? Diálogos con confirmación
? Validaciones de entrada
? Permisos verificados
? Listo para UAT
