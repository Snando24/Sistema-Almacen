# Análisis del error visual tras validar un CSV

## Resumen ejecutivo

El problema no está en la validación del CSV ni en la lógica de negocio; el fallo es de UI/layout en la pantalla de importación. La validación llama a `ImportPage._on_validated()` y, al rellenar la vista previa, la zona inferior del formulario se vuelve inestable y el contenido visual se comprime o desaparece.

La evidencia está en la capa de presentación:

- [src/sisalmacen/ui/pages/import_page.py](src/sisalmacen/ui/pages/import_page.py)
- [src/sisalmacen/ui/widgets.py](src/sisalmacen/ui/widgets.py)
- [src/sisalmacen/ui/theme.py](src/sisalmacen/ui/theme.py)

## Síntomas observados

Tras pulsar “Validar archivo”:

- la cabecera del formulario se mantiene,
- aparecen mensajes de warning/errores,
- la tabla inferior deja de mostrarse bien,
- el texto/etiquetas se vuelven difíciles de leer o se desordenan,
- la pantalla queda con una sensación de “layout roto” aunque la validación haya terminado correctamente.

## Localización probable del problema

### 1) La validación actualiza la vista con contenido dinámico sin reservar espacio suficiente

En [src/sisalmacen/ui/pages/import_page.py](src/sisalmacen/ui/pages/import_page.py), la función `_on_validated()` hace esto:

- reemplaza `_summary`
- reemplaza `_warnings`
- actualiza el modelo de la tabla
- muestra filas de previsualización

El problema es que la parte inferior del formulario se construye como una pila vertical sin un tamaño mínimo explícito ni un `QSplitter`/`QVBoxLayout` con expansión controlada. Cuando el texto de warning o la tabla se hace más grande, el layout intenta reacomodar todo el bloque y la tabla final queda “forzada” fuera del área visible.

Punto crítico:

- `self._summary` y `self._warnings` están en el mismo contenedor vertical que la tabla.
- No hay una separación con un tamaño mínimo para la tabla.
- La tabla se agrega con `layout.addWidget(self._table, 1)`, pero no hay una política de tamaño claro para la tabla cuando el contenido se vuelve largo.

### 2) La tabla se crea sin estrategia de tamaño que soporte contenido variable

En [src/sisalmacen/ui/widgets.py](src/sisalmacen/ui/widgets.py), `make_table()` crea un `QTableView` con un estilo base, pero no define:

- `setMinimumHeight(...)`
- `setSizePolicy(...)`
- `setVerticalScrollBarPolicy(...)`
- altura mínima explícita para el bloque de resultados

Esto significa que cuando aparece el contenido de validación, el QTableView puede reducir su área útil si el layout del formulario ya está muy comprimido.

### 3) El estilo global del tema está reforzando el problema visual

En [src/sisalmacen/ui/theme.py](src/sisalmacen/ui/theme.py), el estilo aplica propiedades globales como:

- `QLabel { color: ... }`
- `QWidget { color: ... }`
- `QTableView { ... border ... }`

Eso no rompe la lógica, pero sí hace que cualquier reflow del layout se vea mucho más agresivo. Si además la etiqueta de warnings se vuelve muy larga o el texto se desborda, el contenedor visual se desordena con facilidad.

## Observación clave de la causa raíz

La regresión visual no parece ser un fallo del parser CSV, sino una mala gestión del espacio del layout en la pantalla de importación cuando la validación devuelve contenido. El flujo “validar → rellenar preview” hace que el formulario se recalcule sin una política de altura/expansión para la tabla y el bloque de mensajes.

## Evidencia del punto de fallo

La secuencia más sospechosa es esta:

1. [src/sisalmacen/ui/pages/import_page.py](src/sisalmacen/ui/pages/import_page.py) crea el bloque de importación, con `self._summary`, `self._warnings` y `self._table` en un mismo `QVBoxLayout`.
2. `_on_validated()` actualiza texto y contenido de la tabla.
3. Nadie fija una altura mínima ni una política de expansión para la tabla ni para la zona de warnings.
4. El layout se recompone y en la pantalla se ve comprimido o desaparecido.

## Hipótesis operativa

El fallo más probable es una combinación de:

- falta de sizing mínimo en la vista previa,
- textos largos de warning/errores que aumentan la altura del bloque,
- ausencia de un `QSplitter` o expansión explícita para la tabla,
- estilo global de Qt que hace más visible el problema visual.

## Recomendación de corrección

Se recomienda:

1. Definir claramente una zona de previsualización con altura mínima para el bloque inferior.
2. Añadir `setSizePolicy` y `setMinimumHeight` al `QTableView`.
3. Mantener `self._warnings` y la tabla en un contenedor dedicado en lugar de mezclarlo con la zona principal del formulario.
4. Separar mensajes de warning de la tabla mediante un `QGroupBox` o un layout secundario.
5. Revisar la política de `QVBoxLayout` para evitar que el label largo “empuje” el panel inferior.

## Conclusión

El problema es de interfaz gráfica y de composición de layout, no de validación de archivos CSV. La validación termina correctamente, pero la pantalla de importación no está dimensionada para soportar el contenido dinámico que se inyecta tras la validación.

Si se quiere corregir de forma robusta, hay que tocar el layout y los tamaños de los widgets de la misma pantalla, sin tocar la lógica del importado en sí.
