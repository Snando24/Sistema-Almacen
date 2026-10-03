# Diagnóstico de desalineación frente al MD de R&R

## 1. Objetivo

Este documento recoge el análisis de compatibilidad entre el estado actual del código y el ajuste de producto/categorías definido en el documento `05_Ajustes_Modelo_Producto_y_Categorias_RR.md`.

No incluye cambios de implementación. Su finalidad es dejar una base clara para continuar con la modificación requerida.

---

## 2. Alcance de comparación

Se comparan principalmente estos artefactos:

- [05_Ajustes_Modelo_Producto_y_Categorias_RR.md](05_Ajustes_Modelo_Producto_y_Categorias_RR.md)
- [04_Decisiones_Arquitectura_y_Reglas.md](04_Decisiones_Arquitectura_y_Reglas.md)
- [db/001_schema.sql](db/001_schema.sql)
- [src/sisalmacen/infrastructure/db/models.py](src/sisalmacen/infrastructure/db/models.py)
- [src/sisalmacen/domain/inventory.py](src/sisalmacen/domain/inventory.py)
- [src/sisalmacen/application/products.py](src/sisalmacen/application/products.py)
- [src/sisalmacen/application/importing.py](src/sisalmacen/application/importing.py)
- [src/sisalmacen/infrastructure/migrations/versions/0003_rr_product_model.py](src/sisalmacen/infrastructure/migrations/versions/0003_rr_product_model.py)

---

## 3. Resumen ejecutivo

El proyecto está en una fase avanzada en el modelo de producto y gestión de inventario, y cumple varias reglas del ajuste R&R:

- La categoría es un atributo explícito del producto.
- El producto tiene `activo` / `inactivo` y no se elimina físicamente.
- El stock se gestiona a partir de movimientos.
- El código externo es opcional y, si falta, se genera un identificador interno.
- Hay soporte para `stock_minimo` con alertas de bajo mínimo.

Sin embargo, no está completamente alineado con el MD R&R porque aún persisten elementos que el ajuste marca como fuera de la operación actual:

- `stock_maximo` sigue presente en el dominio y en la BD.
- La lógica de alertas sigue teniendo una visión de stock máximo.
- El modelo no refleja la evolución a stock multialmacén / multiubicación.
- Existen nombres de estados/alertas que no coinciden exactamente con la terminología propuesta en el MD (`AGOTADO` vs `SIN_STOCK`, `STOCK BAJO` vs `BAJO_MINIMO`).

---

## 4. Elementos que sí están alineados

### 4.1. Categoría explícita y no derivada de colores

Sí está bien resuelto que la categoría sea un atributo del producto y no se derive de colores del Excel.

Evidencias:

- [04_Decisiones_Arquitectura_y_Reglas.md](04_Decisiones_Arquitectura_y_Reglas.md)
- [src/sisalmacen/infrastructure/db/models.py](src/sisalmacen/infrastructure/db/models.py)
- [src/sisalmacen/infrastructure/migrations/versions/0003_rr_product_model.py](src/sisalmacen/infrastructure/migrations/versions/0003_rr_product_model.py)

Conclusión: cumple.

### 4.2. Código opcional con identificador interno

El caso de uso de producto genera un identificador interno cuando el código externo no viene informado.

Evidencias:

- [src/sisalmacen/application/products.py](src/sisalmacen/application/products.py)

Conclusión: cumple.

### 4.3. Estado activo/inactivo y baja lógica

El producto usa `activo` para desactivación y no elimina físicamente el registro.

Evidencias:

- [src/sisalmacen/infrastructure/db/models.py](src/sisalmacen/infrastructure/db/models.py)
- [src/sisalmacen/application/products.py](src/sisalmacen/application/products.py)

Conclusión: cumple.

### 4.4. Stock calculado desde movimientos

La base del modelo sigue la regla de que el stock se calcula por movimientos y no se actualiza directamente en el producto.

Evidencias:

- [src/sisalmacen/infrastructure/db/models.py](src/sisalmacen/infrastructure/db/models.py)
- [src/sisalmacen/application/movements.py](src/sisalmacen/application/movements.py)

Conclusión: cumple.

### 4.5. `stock_minimo` y alertas de bajo nivel

La lógica de mínimo existe y se usa para indicar estado bajo umbral.

Evidencias:

- [src/sisalmacen/domain/inventory.py](src/sisalmacen/domain/inventory.py)
- [src/sisalmacen/ui/dialogs/product_dialog.py](src/sisalmacen/ui/dialogs/product_dialog.py)

Conclusión: parcialmente cumple, pero con nombres y terminología distintos al MD.

---

## 5. Desalineaciones principales

### 5.1. `stock_maximo` sigue existiendo en el modelo

El mayor desajuste es que el campo `stock_maximo` sigue presente en:

- [db/001_schema.sql](db/001_schema.sql)
- [src/sisalmacen/infrastructure/db/models.py](src/sisalmacen/infrastructure/db/models.py)
- [src/sisalmacen/domain/inventory.py](src/sisalmacen/domain/inventory.py)
- [src/sisalmacen/application/products.py](src/sisalmacen/application/products.py)

El MD R&R indica explícitamente que se desactiva el uso operativo de stock máximo y que no debe participar en validaciones, alertas ni reportes.

Conclusión: no cumple el requisito de “sin stock máximo operativo”.

### 5.2. Alertas siguen pensadas con la lógica de máximo

El dominio define:

- `SIN_STOCK`
- `BAJO_MINIMO`
- `SOBRE_MAXIMO`

Esto se ve en:

- [src/sisalmacen/domain/inventory.py](src/sisalmacen/domain/inventory.py)

El MD R&R propone un esquema más simple:

- `AGOTADO` si `stock_actual <= 0`
- `STOCK BAJO` si `stock_actual <= stock_minimo`
- `SIN CONFIGURAR` si no hay mínimo
- sin stock máximo

Conclusión: las alertas están parcialmente alineadas, pero conceptualmente no coinciden con el nuevo modelo deseado.

### 5.3. No hay soporte de stock por almacén/ubicación

El MD R&R precisa que, si el cliente en el futuro maneja más de un almacén o ubicación, el stock debe almacenarse como relación `producto + almacen/ubicación` y no como un único valor del producto.

Sin embargo, el código actual sigue con una estructura de inventario por producto único:

- [src/sisalmacen/infrastructure/db/models.py](src/sisalmacen/infrastructure/db/models.py)

Se mantienen:

- `inventario(producto_id)`
- `producto.ubicacion_id`
- `ubicacion` como atributo del producto

Conclusión: no cumple la evolución que el MD propone para escenarios multialmacén.

### 5.4. La terminología del MD no está 100% reflejada en la UI y reportes

El ajuste R&R usa conceptos como:

- `AGOTADO`
- `STOCK BAJO`
- `SIN CONFIGURAR`

El código actual usa:

- `Sin stock`
- `Bajo mínimo`
- `Sin configurar`
- y aún contempla `Sobre máximo`

Esto no es un bug funcional grave, pero sí genera una desalineación semántica respecto a la normativa del documento de negocio.

Conclusión: requiere normalización terminológica.

---

## 6. Qué falta para continuar con la modificación

### Prioridad 1: quitar el stock máximo del modelo funcional

Tareas propuestas:

1. Eliminar `stock_maximo` de las entidades de dominio y repositorios.
2. Eliminar la validación `stock_maximo < stock_minimo`.
3. Quitar alertas de “sobre máximo” en UI y reportes.
4. Eliminar el campo del esquema y de las migraciones si se desea dejar el modelo limpio.

### Prioridad 2: normalizar reglas de alerta a la semántica del MD

Definir exactamente:

- `AGOTADO` si `cantidad <= 0`
- `STOCK BAJO` si `cantidad <= stock_minimo` y `cantidad > 0`
- `SIN CONFIGURAR` si `stock_minimo` es nulo

Esto implica alinear código y textos de la interfaz.

### Prioridad 3: preparar la evolución de multialmacén

No se debe implementar aún como MVP si la decisión es mantener un único almacén; pero sí deben dejarse las bases para que no se vuelva a introducir un modelo restrictivo.

Tareas recomendadas:

- documentar claramente que `inventario(producto_id)` es un diseño actual del MVP,
- separar la noción de `almacén` y `ubicación` del producto,
- dejar un punto de extensión para `inventario(producto_id, almacen_id, ubicacion_id)`.

### Prioridad 4: validar el CSV de importación frente al nuevo modelo

El flujo de importación ya soporta categorías y stock mínimo, pero debe revisarse si el CSV real del cliente seguirá encajando exactamente con:

- `categoria` obligatoria,
- `stock_minimo` opcional,
- `codigo` opcional,
- `unidad` y `precio` opcionales según regla de negocio.

---

## 7. Conclusión final

El proyecto ya ha avanzado más allá del punto de “modelo básico”; tiene un diseño sólido para producto, movimientos, auditoría y catálogo.

Sin embargo, la desalineación real con el MD R&R es clara:

- no está totalmente retirado el concepto de stock máximo,
- la lógica de alertas no coincide exactamente con la semántica pedida,
- y el modelo de stock por almacén/ubicación aún no está preparado para la evolución futura.

Por tanto, el código no está “listo” para cerrar la modificación del MD como una coincidencia total, pero sí está muy cerca de la línea base funcional del proyecto.

El siguiente paso lógico es una corrección de modelo y semántica, no una reescritura completa del sistema.
