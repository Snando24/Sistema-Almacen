# Flujos Incorrectos - Importación CSV

## Resumen Ejecutivo

La pantalla de importación CSV actual tiene estos flujos **INCORRECTOS** o **INCOMPLETOS**:

---

## FLUJO 1: Seleccionar Archivo

### ? ACTUAL (INCORRECTO)
```
Usuario selecciona CSV
        ?
archivo guardado en self._path
        ?
(no hay limpie de resultados anteriores)
        ?
Validar botón habilitado
```

### ? ESPERADO (Documento 11, §4)
```
Usuario selecciona CSV
        ?
1. Guardar ruta seleccionada
2. Limpiar resultados de validación anterior
3. Limpiar tabla preview/errores
4. Limpiar mensajes
5. Estado ? ARCHIVO_SELECCIONADO
6. Habilitar Validar
7. Mantener Aplicar deshabilitado
```

### Problema
- Restos de validaciones anteriores pueden "contaminar" la nueva

---

## FLUJO 2: Validar Archivo

### ? ACTUAL (INCORRECTO)
```
Usuario pulsa Validar
        ?
mensaje "Validando archivo..."
        ?
ejecutar validación
        ?
si error ? excepción
        ?
mensaje NO desaparece
interfaz bloqueada/inconsistente
```

### ? ESPERADO (Documento 11, §5-6)
```
Usuario pulsa Validar
        ?
verificar archivo existe
verificar extensión .csv
limpiar resultados anteriores
Estado ? VALIDANDO
        ?
Validando archivo...
Desabilitar controles
        ?
try:
    validar()
catch error:
    mostrar error controlado
finally:
    ?? GARANTIZADO desaparecer mensaje
    ?? GARANTIZADO finalizar VALIDANDO
    ?? GARANTIZADO actualizar botones
    ?? GARANTIZADO restaurar cursor
```

### Problemas
- ? Sin `finally` ? mensajes pegados
- ? Sin try-catch ? excepciones sin controlar
- ? Botones no se restauran si error

---

## FLUJO 3: Resultado de Validación CORRECTO

### ? ACTUAL (POSIBLE)
```
Validación exitosa
        ?
mensaje breve
Aplicar está habilitado
(quizá con estado visual débil)
```

### ? ESPERADO (Documento 11, §7)
```
Estado ? VALIDO
        ?
Mostrar:
"Archivo validado correctamente.
 Registros: 230
 Nuevos: 230
 Actualizaciones: 0
 Errores: 0"
        ?
Acciones:
- ? Habilitar Aplicar
- ? Mantener Descartar habilitado
- ? Mostrar previsualización
- ? Permitir revalidar
        ?
Mensaje desaparece
```

### Problema
- No hay resumen visual claro

---

## FLUJO 4: Resultado de Validación CON ERRORES

### ? ACTUAL (POSIBLE)
```
Validación con errores
        ?
tabla roja
Aplicar permanece desabilitado
(pero no hay opción de omitir)
```

### ? ESPERADO (Documento 11, §8)
```
Estado ? CON_ERRORES
        ?
Mostrar:
"Archivo validado con errores.
 Registros: 230
 Válidos: 228
 Errores: 2"
        ?
Tabla roja con:
| Fila | Código | Acción | Detalle |
| 25   | RR-025 | ERROR  | Falta descripción |
| 81   | RR-081 | ERROR  | Stock mínimo inválido |
        ?
Aplicar deshabilitado
        ?
[?] Omitir errores (solo ADMIN)
    ? Habilitaría Aplicar
```

### Problemas
- Tabla puede no mostrar contexto adecuado

---

## FLUJO 5: Error Inesperado en Validación

### ? ACTUAL (PROBABLE)
```
Error técnico ocurre
        ?
stack trace en consola
interfaz confundida
usuario atrapado
requiere reiniciar app
```

### ? ESPERADO (Documento 11, §9)
```
Excepción lanzada
        ?
try-catch nivel superior
        ?
Mostrar al usuario:
"No se pudo validar el archivo.
 Revise el formato o consulte el registro de errores."
        ?
Registrar detalle en logs
NO mostrar stack trace
        ?
finally:
- Finalizar VALIDANDO
- Habilitar Validar de nuevo
- Mantener archivo seleccionado
- Mantener Descartar habilitado
- Desabilitar Aplicar
```

### Problemas
- ? Sin manejo de excepción controlada
- ? Usuario sin recuperación

---

## FLUJO 6: Botón Descartar

### ? ACTUAL (PROBABLE)
```
Usuario pulsa Descartar
        ?
si preview == null
    ? NullPointerException
    
si no hay errores guardados
    ? AttributeError
    
si se llama dos veces
    ? error
```

### ? ESPERADO (Documento 11, §10-11)
```
Usuario pulsa Descartar
        ?
Operación SIEMPRE exitosa
(idempotente)
        ?
Limpiar:
? archivo seleccionado
? ruta mostrada
? tabla resultados
? mensajes estado
? errores
? estadísticas validación
? opciones a inicial
        ?
Desabilitar Aplicar
Desabilitar Validar
Habilitar Seleccionar archivo
        ?
Estado ? SIN_ARCHIVO
        ?
Validar dos veces = validar una vez
Descartar dos veces = descartar una vez
```

### Problemas
- ? Sin protección contra nulos
- ? NO es idempotente

---

## FLUJO 7: Doble Clic en Validar

### ? ACTUAL (PROBABLE)
```
Usuario pulsa Validar
        ?
comienza validación
        ?
Usuario pulsa Validar OTRA VEZ
        ?
DOS validaciones simultáneas
        ?
condición de carrera
datos corruptos
```

### ? ESPERADO (Documento 11, §13)
```
Usuario pulsa Validar
        ?
Botón Validar ? DESHABILITADO
        ?
Validar ejecuta
        ?
Botón Validar ? HABILITADO
        ?
segundo clic en Validar ? sin efecto
(botón estaba deshabilitado)
```

### Problemas
- ? Prevención de doble clic NO está implementada

---

## FLUJO 8: Cambiar Archivo Después de Validar

### ? ACTUAL (PROBABLE)
```
Usuario valida CSV1
        ?
archivo CSV1 validado
        ?
Usuario selecciona CSV2
        ?
preview CSV1 PERMANECE
        ?
Usuario pulsa Aplicar
        ?
se aplica CSV1 (¡INCORRECTO!)
```

### ? ESPERADO (Documento 11, §14)
```
Usuario valida CSV1
        ?
archivo CSV1 validado
        ?
Usuario selecciona CSV2
        ?
1. Limpiar preview CSV1
2. Limpiar errores
3. Aplicar ? DESHABILITADO
4. Estado ? ARCHIVO_SELECCIONADO
5. Exigir revalidar CSV2
```

### Problemas
- ? No hay invalidación automática

---

## FLUJO 9: Cambiar Opciones Después de Validar

### ? ACTUAL (PROBABLE)
```
Usuario valida con:
- Modo: INSERTAR
- Separador: coma
- Decimal: punto
        ?
preview mostrado
        ?
Usuario CAMBIA separador a punto y coma
        ?
preview VIEJO permanece
        ?
Aplicar con nuevos parámetros
        ?
datos incorrectos aplicados
```

### ? ESPERADO (Documento 11, §15)
```
Usuario valida con parámetros X
        ?
preview mostrado
        ?
Usuario CAMBIA:
- codificación
- separador
- separador decimal
- modo
- crear catálogos
- aplicar stock
- omitir errores
        ?
validación anterior INVÁLIDA
        ?
1. Volver a ARCHIVO_SELECCIONADO
2. Limpiar preview
3. Desabilitar Aplicar
4. Exigir revalidar
```

### Problemas
- ? Sin listeners en controles de opciones
- ? Sin invalidación automática

---

## FLUJO 10: Aplicar Importación

### ? ACTUAL (PROBABLE)
```
Usuario pulsa Aplicar
        ?
barra de progreso visible
texto "Aplicando importación..."
        ?
comienza importación
        ?
si error ? excepción
        ?
barra y texto QUEDAN VISIBLES
estado indefinido
```

### ? ESPERADO (Documento 11, §12)
```
User pulsa Aplicar
        ?
Solo si Estado == VALIDO
O (Estado == CON_ERRORES AND ADMIN AND omitir_errores)
        ?
Estado ? APLICANDO
        ?
Mostrar: "Aplicando importación..."
Desabilitar todos los controles
        ?
try:
    transacción()
catch error:
    mostrar error
finally:
    Estado ? COMPLETADO
    mensaje desaparece
    botones se restauran
```

### Problemas
- ? Sin try-finally
- ? Sin estado APLICANDO
- ? Mensajes temporales pueden quedar pegados

---

## FLUJO 11: Tabla de Estados y Control de Botones

### ? ACTUAL (PROBABLE)
```
Estado: ?
Botones: enabled/disabled de forma inconsistente
Transiciones: no definidas
```

### ? ESPERADO (Documento 11, §19)

| Estado | Validar | Aplicar | Descartar | Seleccionar |
|---|---:|---:|---:|---:|
| SIN_ARCHIVO | ? | ? | ?* | ? |
| ARCHIVO_SELECCIONADO | ? | ? | ? | ? |
| VALIDANDO | ? | ? | ?/Cancelar | ? |
| VALIDO | ? | ? | ? | ? |
| CON_ERRORES | ? | ?** | ? | ? |
| APLICANDO | ? | ? | ? | ? |
| COMPLETADO | ? | ? | ? | ? |

\* Descartar en SIN_ARCHIVO no falla; simplemente no hace nada  
\*\* Puede habilitarse solo para ADMIN con "Omitir filas con error"

### Problemas
- ? Tabla de control NO está implementada

---

## MATRIZ DE PROBLEMAS DE FLUJO

| Flujo | Gravedad | Estado Actual | Estado Esperado | Causa |
|---|---|---|---|---|
| 1. Seleccionar | MEDIA | Incompleto | ARCHIVO_SELECCIONADO | Falta cleanup |
| 2. Validar | CRÍTICA | Sin finally | try-catch-finally | Mensajes pegados |
| 3. Correcto | MEDIA | Débil | VALIDO + resumen | UI pobre |
| 4. Con errores | MEDIA | Posible | CON_ERRORES + detalle | UI pobre |
| 5. Error | CRÍTICA | Sin catch | Manejo controlado | Sin recuperación |
| 6. Descartar | CRÍTICA | No idempotente | Idempotente | Falta validar nulos |
| 7. Doble clic | CRÍTICA | No prevenido | Botón desabilitado | Falta lock |
| 8. Cambiar archivo | ALTA | No invalida | Invalida automático | Falta listener |
| 9. Cambiar opciones | ALTA | No invalida | Invalida automático | Falta listener |
| 10. Aplicar | CRÍTICA | Sin finally | try-finally | Mensajes pegados |
| 11. Control botones | CRÍTICA | Ad-hoc | Por máquina estados | Falta estructura |

---

## CONCLUSION

**11 de 11 flujos tienen problemas.**

**Severidad total: CRÍTICA**

La pantalla de importación CSV **NO es usable en su forma actual** si se siguen las especificaciones de los documentos 10 y 11.

Requiere rediseño completo de:
1. ? Máquina de estados (Flujo 1, 8, 9, 11)
2. ? Try-catch-finally (Flujo 2, 5, 10)
3. ? Idempotencia (Flujo 6)
4. ? Prevención de condición de carrera (Flujo 7)
5. ? Validación de datos (Flujo 3, 4)
6. ? Mensajes temporales garantizados (Flujo 2, 5, 10)
