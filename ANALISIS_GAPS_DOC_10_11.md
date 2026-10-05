# Análisis GAPs - Comparación Especificación vs Implementación Actual

**Fecha:** 2026-10-05  
**Documentos de referencia:** 10_Correccion_Importador_CSV_Productos_Movimientos.md, 11_Correcciones_Flujo_Estados_Importacion_CSV.md

---

## RESUMEN EJECUTIVO

La implementación actual de importación/exportación CSV tiene **discrepancias críticas** con la especificación final. Se identifi

can:

- **5 GAPs principales** en estructura de datos
- **3 GAPs** en flujo de estados de interfaz
- **2 GAPs** en validación por tipo de archivo
- **1 GAP** en manejo de stock

---

## GAP-001: Campos obligatorios INCORRECTO

### Estado Actual (MALO)
```python
# src/sisalmacen/domain/importing.py línea 35
REQUIRED_FOR_INSERT = ("nombre", "categoria", "unidad")
```

### Especificación (Documento 10, §5)
```
Para PRODUCTOS:
Obligatorios mínimos:
- codigo_producto  
- descripcion

NO debe exigir: nombre, categoria, unidad
```

### Impacto
? Usuarios no pueden importar Productos_RR_App.csv  
? Mensaje de error: "Faltan columnas obligatorias: nombre, unidad."

---

## GAP-002: Estructura de columnas INCORRECTO

### Estado Actual (MALO)
```python
# src/sisalmacen/domain/importing.py línea 18-31
COLUMNS = (
    "codigo",
    "nombre",
    "categoria",
    "unidad",
    "codigo_barras",
    "descripcion",
    "marca",
    "proveedor",
    "ubicacion",
    "precio_compra",
    "precio_venta",
    "stock_minimo",
    "stock",           # ? INCORRECTO
    "estado",
    "observaciones",
)
```

### Especificación (Documento 10, §4)
```
PRODUCTOS debe tener:
- codigo_producto
- descripcion
- descripcion_adicional
- marca
- categoria
- precio_compra
- precio_venta
- stock_minimo
- stock_inicial      # ? NUEVO
- entradas           # ? NUEVO
- salidas            # ? NUEVO
- stock_actual       # ? NUEVO (NO "stock")
- almacen
- ubicacion
- proveedor
- fecha_registro
- estado
- observacion
```

### Impacto
? CSV con columnas modernas (`stock_inicial`, `entradas`, `salidas`, `stock_actual`) no se reconocen  
? Lógica antigua de columna genérica `stock` no aplica al modelo final

---

## GAP-003: No hay separación de validadores por tipo

### Estado Actual
- Un único validador genérico para todos los CSVs
- No diferencia entre PRODUCTOS y MOVIMIENTOS

### Especificación (Documento 10, §2 y Documento 11, §17)
```
Debe existir:
1. Validador específico para PRODUCTOS
   Obligatorios: codigo_producto, descripcion

2. Validador específico para MOVIMIENTOS
   Obligatorios: tipo_movimiento, fecha, codigo_producto, cantidad, um
```

### Impacto
? No se pueden importar Movimientos con validación correcta  
? Pantalla no sabe qué tipo de archivo se está importando  
? Reglas de negocio diferentes no se pueden aplicar

---

## GAP-004: No hay máquina de estados en UI

### Especificación (Documento 11, §3)
```
Estados requeridos:
SIN_ARCHIVO
ARCHIVO_SELECCIONADO
VALIDANDO
VALIDO
CON_ERRORES
APLICANDO
COMPLETADO
```

### Estado Actual
- No existe máquina de estados explícita
- Usa flags independientes (`_preview`, `_import_id`, `_has_errors`)
- Pueden quedarse desincronizados

### Impacto
? Mensaje "Validando archivo..." puede quedar pegado  
? Botones pueden estar habilitados/deshabilitados incorrectamente  
? Excepciones pueden bloquear interfaz

---

## GAP-005: Descarte no es idempotente

### Especificación (Documento 11, §10)
```
Descartar DEBE ser idempotente:
- Pulsar dos veces = pulsar una vez
- NO debe fallar aunque no exista preview
- NO debe lanzar excepción si preview es nulo
```

### Estado Actual (Probable)
- No hay protección contra nulos
- Puede fallar si validación anterior no completó
- No está garantizado el cleanup completo

### Impacto
? Usuario queda atrapado si ocurre excepción  
? Requiere reiniciar la aplicación en casos de error

---

## GAP-006: Stock vacío se convierte en cero

### Especificación (Documento 10, §13-14)
```
Si stock_actual está vacío:
? NO convertir a 0
? Tratar como STOCK PENDIENTE

Si stock_actual = 0 explícitamente:
? Registrar como 0
? Marcar como AGOTADO (no INACTIVO)
```

### Estado Actual (Probable)
- No hay distinción entre vacío y cero
- Puede asignar 0 automáticamente

### Impacto
? Datos de stock perdidos/corrompidos  
? Inventario no es confiable post-importación

---

## GAP-007: No hay soporte para importación histórica sin impacto en stock

### Especificación (Documento 10, §22 y Documento 11, §18)
```
Opción requerida en Movimientos:
[ ] Importar como historial sin afectar stock

Cuando está activada:
- Movimiento se registra
- Queda visible en Kardex
- NO incrementa/disminuye stock actual
```

### Estado Actual
- No existe esta opción
- Toda importación afecta el stock

### Impacto
? Archivo histórico duplicaría stock si se importa directamente  
? No hay forma de migrar Movimientos_RR_App.csv sin afectar saldo

---

## GAP-008: Opción "Aplicar stock" es antigua

### Especificación (Documento 10, §11-12 y Documento 11, §16)
```
Opción actual (INCORRECTA):
[?] Aplicar stock de la columna «stock» (genera movimientos)

Debe ser (CORRECTA):
[?] Aplicar stock_actual como saldo de migración
  Texto: Crea el saldo inicial del producto utilizando la columna stock_actual.
         Las columnas stock_inicial, entradas y salidas se conservan como información histórica.
```

### Estado Actual
```python
# src/sisalmacen/ui/pages/import_page.py
self._apply_stock = QCheckBox("Aplicar stock de la columna «stock» (genera movimientos)")
```

### Impacto
? Duplica stock si se usa con archivo CSV nuevo  
? Mensaje es confuso/incorrecto

---

## GAP-009: Cambio de archivo/opciones no invalida validación

### Especificación (Documento 11, §14-15)
```
Si usuario cambia:
- archivo
- codificación
- separador
- separador decimal
- modo insertar/actualizar
- crear catálogos
- aplicar stock
- omitir errores

? Validación anterior se vuelve INVÁLIDA
? Volver a estado ARCHIVO_SELECCIONADO
? Exigir revalidar antes de aplicar
```

### Estado Actual (Probable)
- No hay invalidación automática
- Usuario podría aplicar resultados obsoletos

### Impacto
? Aplicar con parámetros diferentes a los validados  
? Datos inconsistentes en base de datos

---

## GAP-010: Validación de encabezados por posición

### Especificación (Documento 10, §25)
```
Validación de encabezados DEBE:
- Validar por NOMBRE, no por posición
- Aceptar cualquier orden de columnas
- Ignorar mayúsculas/minúsculas
- Eliminar espacios externos
- Permitir UTF-8 y tildes
```

### Impacto
? CSV con columnas reordenadas se rechaza  
? Menor flexibilidad que sistemas profesionales

---

## MATRIZ DE CAMBIOS REQUERIDOS

| ID | GAP | Severidad | Componente | Acción |
|---|---|---|---|---|
| CR-01 | 001 | CRÍTICA | domain/importing.py | Cambiar REQUIRED_FOR_INSERT |
| CR-02 | 002 | CRÍTICA | domain/importing.py | Reemplazar COLUMNS |
| CR-03 | 003 | CRÍTICA | application/importing.py | Separar validadores |
| CR-04 | 004 | CRÍTICA | ui/pages/import_page.py | Implementar máquina de estados |
| CR-05 | 005 | ALTA | ui/pages/import_page.py | Hacer Descartar idempotente |
| CR-06 | 006 | ALTA | application/importing.py | Validar stock vacío vs cero |
| CR-07 | 007 | MEDIA | ui/pages/import_page.py | Agregar opción "sin afectar stock" |
| CR-08 | 008 | MEDIA | ui/pages/import_page.py | Actualizar label de "Aplicar stock" |
| CR-09 | 009 | MEDIA | ui/pages/import_page.py | Invalidar validación al cambiar parámetros |
| CR-10 | 010 | BAJA | application/importing.py | Validar encabezados por nombre |

---

## ORDEN DE IMPLEMENTACIÓN RECOMENDADO

### Fase 1 (BLOQUEADORA - Hoy)
1. CR-01: Cambiar REQUIRED_FOR_INSERT
2. CR-02: Reemplazar COLUMNS con estructura moderno
3. CR-03: Separar validadores Productos/Movimientos

### Fase 2 (CRÍTICA - Hoy)
4. CR-04: Máquina de estados en UI
5. CR-05: Idempotencia de Descartar

### Fase 3 (ALTA - Próxima iteración)
6. CR-06: Validación de stock
7. CR-09: Invalidación automática

### Fase 4 (MEDIA - Próxima iteración)
8. CR-07: Opción histórica
9. CR-08: Label actualizado
10. CR-10: Validación por nombre

---

## CONCLUSIÓN

**La implementación actual NO es compatible con la especificación.**

La arquitectura CSV necesita:
1. ? Redefinir estructura de datos (campos, obligatorios)
2. ? Separar validadores por tipo de archivo
3. ? Implementar máquina de estados en UI
4. ? Manejar casos excepcionales (errores, cambios, nulos)

**Estimado de esfuerzo:** 3-4 sesiones de desarrollo  
**Riesgo de no implementar:** Sistema de importación no usable

