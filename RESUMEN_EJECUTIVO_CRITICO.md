# ?? RESUMEN EJECUTIVO - REVISIÓN CRÍTICA

**Fecha:** 2026-10-05  
**Revisión de:** Documentos 10 y 11 vs Implementación Actual  
**Status:** ? NO CONFORME - Requiere correcciones críticas

---

## HALLAZGOS

### Severidad General: ?? CRÍTICA

La implementación actual del sistema CSV tiene **discrepancias significativas** con la especificación de Documentos 10 y 11.

- **10 GAPs identificados** en estructura de datos y validación
- **11 flujos de interfaz incorrectos** en la pantalla de importación
- **1 arquitectura de estado faltante** que afecta todo

---

## TOP 5 PROBLEMAS CRÍTICOS

| # | Problema | Impacto | Componente |
|---|---|---|---|
| **1** | REQUIRED_FOR_INSERT = ("nombre", "categoria", "unidad") en lugar de ("codigo_producto", "descripcion") | ? No importa Productos_RR_App.csv | domain/importing.py |
| **2** | Estructura COLUMNS desactualizada (falta stock_inicial, entradas, salidas, stock_actual) | ? CSV moderno no se reconoce | domain/importing.py |
| **3** | Sin máquina de estados en UI (falta SIN_ARCHIVO, VALIDANDO, VALIDO, CON_ERRORES, etc.) | ? Interfaz inconsistente, mensajes pegados | ui/pages/import_page.py |
| **4** | Sin separación de validadores Productos vs Movimientos | ? No puede validar Movimientos correctamente | application/importing.py |
| **5** | Método Descartar no es idempotente (puede fallar si preview es nulo) | ? Interfaz se bloquea, requiere reiniciar app | ui/pages/import_page.py |

---

## DOCUMENTOS GENERADOS

Se han creado 2 documentos con análisis completo:

### 1. ?? ANALISIS_GAPS_DOC_10_11.md
- Detalla 10 GAPs específicos (GAP-001 a GAP-010)
- Incluye estado actual vs esperado para cada uno
- Matriz de cambios requeridos (CR-01 a CR-10)
- Plan de implementación en 4 fases

### 2. ?? FLUJOS_INCORRECTOS_IMPORTACION.md
- Analiza 11 flujos de la pantalla de importación
- Muestra estado actual (?) vs esperado (?) para cada uno
- Identifica la causa raíz de cada problema
- Matriz de severidad de flujos

---

## TABLA COMPARATIVA RÁPIDA

### Estructura de Datos

| Aspecto | Actual ? | Esperado ? |
|---------|----------|------------|
| Obligatorios Productos | "nombre", "categoria", "unidad" | "codigo_producto", "descripcion" |
| Columna stock | "stock" genérica | "stock_inicial", "entradas", "salidas", "stock_actual" |
| Campo unidad en Producto | Requerido | NO requerido |
| Campo unidad en Movimiento | No existe | Requerido ("um") |

### Estados de UI

| Aspecto | Actual ? | Esperado ? |
|---------|----------|------------|
| Máquina de estados | No existe | 7 estados (SIN_ARCHIVO, ARCHIVO_SELECCIONADO, VALIDANDO, VALIDO, CON_ERRORES, APLICANDO, COMPLETADO) |
| Mensajes "Validando..." | Puede quedar pegado | Garantizado desaparecer (try-finally) |
| Descartar idempotente | No | Sí (validar nulos) |
| Doble-clic prevención | No | Sí (botón deshabilitado) |
| Invalidación automática | No | Sí (al cambiar archivo/opciones) |

### Validadores

| Aspecto | Actual ? | Esperado ? |
|---------|----------|------------|
| Tipo de archivo | Un validador genérico | Validador Productos + Validador Movimientos |
| Flexibilidad orden columnas | Por posición (frágil) | Por nombre (robusto) |
| Stock vacío | Convierte a 0 | Marca como "pendiente" |
| Importación histórica | No existe | Opción "sin afectar stock" |

---

## IMPACTO EN USUARIO FINAL

### Hoy (? Actual)
```
Usuario intenta importar Productos_RR_App.csv
        ?
ERROR: "Faltan columnas obligatorias: nombre, unidad."
        ?
Usuario confundido
        ?
Llamada a soporte
        ?
Sistema no usado
```

### Después de correcciones (? Esperado)
```
Usuario importa Productos_RR_App.csv
        ?
Validar ? "Archivo validado: 230 registros"
        ?
Aplicar ? "Importación completada: 230 insertados"
        ?
Sistema operativo
```

---

## CAMBIOS REQUERIDOS (Orden de Implementación)

### ?? FASE 1 (BLOQUEADORA - Hoy)

**CR-01:** Cambiar `REQUIRED_FOR_INSERT` en domain/importing.py
```python
# De:
REQUIRED_FOR_INSERT = ("nombre", "categoria", "unidad")

# A:
REQUIRED_FOR_INSERT = ("codigo_producto", "descripcion")  # Para PRODUCTOS
REQUIRED_FOR_MOVEMENT = ("tipo_movimiento", "fecha", "codigo_producto", "cantidad", "um")  # Para MOVIMIENTOS
```

**CR-02:** Reemplazar `COLUMNS` en domain/importing.py
```python
# De: ("codigo", "nombre", "categoria", "unidad", ..., "stock", "observaciones")

# A (PRODUCTOS):
COLUMNS_PRODUCTOS = (
    "codigo_producto", "descripcion", "descripcion_adicional", "marca", "categoria",
    "precio_compra", "precio_venta", "stock_minimo", "stock_inicial", "entradas",
    "salidas", "stock_actual", "almacen", "ubicacion", "proveedor", "fecha_registro",
    "estado", "observacion"
)

# A (MOVIMIENTOS):
COLUMNS_MOVIMIENTOS = (
    "tipo_movimiento", "fecha", "codigo_producto", "descripcion", "cantidad", "um",
    "documento", "almacen", "ubicacion", "proveedor", "observacion"
)
```

**CR-03:** Separar validadores en application/importing.py
```python
class ProductosValidator:
    def validate(self, rows, options) -> list[RowResult]:
        # Validar solo para PRODUCTOS

class MovimientosValidator:
    def validate(self, rows, options) -> list[RowResult]:
        # Validar solo para MOVIMIENTOS
```

### ?? FASE 2 (CRÍTICA - Hoy)

**CR-04:** Máquina de estados en ui/pages/import_page.py
```python
class ImportState(Enum):
    SIN_ARCHIVO = "sin_archivo"
    ARCHIVO_SELECCIONADO = "archivo_seleccionado"
    VALIDANDO = "validando"
    VALIDO = "valido"
    CON_ERRORES = "con_errores"
    APLICANDO = "aplicando"
    COMPLETADO = "completado"

class ImportPage:
    def __init__(self):
        self._state = ImportState.SIN_ARCHIVO
        # En lugar de: self._preview, self._import_id, self._has_errors
```

**CR-05:** Idempotencia de Descartar
```python
def _discard(self) -> None:
    try:
        if self._preview is not None:
            self._preview = None
        if self._model is not None:
            self._model.clear()
        # ... limpiar otros campos
    except:
        pass  # Idempotente: no fallar nunca
    finally:
        self._state = ImportState.SIN_ARCHIVO
        self._update_buttons()
```

### ?? FASE 3 (ALTA - Próxima sesión)

**CR-06:** Validar stock vacío vs cero  
**CR-09:** Invalidar automáticamente al cambiar archivo/opciones

### ?? FASE 4 (MEDIA - Próxima sesión)

**CR-07, CR-08, CR-10:** Mejoras funcionales

---

## RECOMENDACIÓN

### ? Realizar AHORA

1. Implementar CR-01, CR-02, CR-03 (cambios en domain y application)
2. Implementar CR-04, CR-05 (máquina de estados y idempotencia)
3. Revisar y ajustar todos los 11 flujos de interfaz

### ?? Validar después

- Suite de tests actualizada
- UAT con archivos Productos_RR_App.csv y Movimientos_RR_App.csv
- Verificar que "Validando..." siempre desaparece
- Verificar que Descartar nunca falla

### ? Futuro (Backlog)

- CR-07: Opción "Importar como historial sin afectar stock"
- Mejora de mensajes y validaciones
- Validación de encabezados por nombre (no posición)

---

## CONCLUSIÓN

La implementación actual **NO ES UTILIZABLE** con la especificación de Documentos 10 y 11.

Se requieren cambios estructurales en:
1. ? **Estructura de datos** (campos obligatorios, columnas)
2. ? **Validadores** (separados por tipo)
3. ? **UI** (máquina de estados, manejo de errores)

**Esfuerzo estimado:** 4-5 horas de desarrollo  
**Riesgo de no implementar:** Sistema de importación no funcional

---

## REFERENCIAS

- [ANALISIS_GAPS_DOC_10_11.md](ANALISIS_GAPS_DOC_10_11.md) - Detalle técnico de cada GAP
- [FLUJOS_INCORRECTOS_IMPORTACION.md](FLUJOS_INCORRECTOS_IMPORTACION.md) - Análisis de flujos de interfaz
- [10_Correccion_Importador_CSV_Productos_Movimientos.md](../../downloads/10_Correccion_Importador_CSV_Productos_Movimientos.md) - Especificación origen
- [11_Correcciones_Flujo_Estados_Importacion_CSV.md](../../downloads/11_Correcciones_Flujo_Estados_Importacion_CSV.md) - Especificación origen

