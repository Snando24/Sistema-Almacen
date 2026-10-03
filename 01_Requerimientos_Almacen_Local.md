# Documento de Requerimientos â€” Sistema de GestiÃ³n de AlmacÃ©n

## Escenario A: AplicaciÃ³n de escritorio local / una sola estaciÃ³n

**VersiÃ³n:** 1.0  
**Estado:** Borrador funcional para validaciÃ³n  
**Fecha:** 2026-10-03  
**Objetivo del documento:** definir el alcance funcional, reglas de negocio, requerimientos no funcionales, criterios de aceptaciÃ³n y modelo preliminar para una aplicaciÃ³n de escritorio orientada a la gestiÃ³n de un almacÃ©n trabajando principalmente en una sola computadora.

---

# 1. Objetivo del sistema

Desarrollar una aplicaciÃ³n de escritorio que permita registrar, consultar, actualizar y controlar la informaciÃ³n de productos e inventario de un almacÃ©n, incluyendo carga masiva desde archivos CSV, gestiÃ³n de movimientos, filtros, alertas, exportaciones a Excel/PDF, auditorÃ­a bÃ¡sica y respaldos de informaciÃ³n.

La soluciÃ³n deberÃ¡ poder operar localmente sin requerir conexiÃ³n permanente a Internet.

---

# 2. Alcance

## 2.1 Incluido en el MVP

- Inicio de sesiÃ³n local.
- GestiÃ³n de productos.
- GestiÃ³n de categorÃ­as.
- GestiÃ³n de marcas.
- GestiÃ³n de unidades de medida.
- GestiÃ³n de proveedores.
- GestiÃ³n de ubicaciones fÃ­sicas del almacÃ©n.
- Control de inventario.
- Entradas de inventario.
- Salidas de inventario.
- Ajustes de inventario.
- ImportaciÃ³n masiva desde CSV.
- ValidaciÃ³n previa de archivos CSV.
- ActualizaciÃ³n de productos existentes mediante CSV.
- Registro de productos nuevos mediante CSV, segÃºn configuraciÃ³n.
- Historial de importaciones.
- BÃºsqueda y filtros.
- Alertas de inventario.
- ExportaciÃ³n a CSV.
- ExportaciÃ³n a Excel.
- ExportaciÃ³n a PDF.
- Vista previa de impresiÃ³n.
- AuditorÃ­a de operaciones relevantes.
- Copias de seguridad manuales.
- RestauraciÃ³n de copias de seguridad.
- ConfiguraciÃ³n bÃ¡sica del sistema.

## 2.2 Fuera del MVP inicial

Quedan previstos para futuras versiones:

- MÃºltiples almacenes.
- SincronizaciÃ³n entre varias computadoras.
- AplicaciÃ³n web.
- AplicaciÃ³n mÃ³vil.
- IntegraciÃ³n con ERP o sistemas contables.
- Compras y Ã³rdenes de compra completas.
- Ventas y facturaciÃ³n.
- PronÃ³stico automÃ¡tico de demanda.
- IntegraciÃ³n con lectores de cÃ³digo de barras.
- IntegraciÃ³n con impresoras de etiquetas.
- Notificaciones por correo, WhatsApp o SMS.
- GestiÃ³n avanzada de lotes y series, salvo que el negocio confirme su necesidad.

---

# 3. Actores

## ACT-01 â€” Administrador

Responsable de la configuraciÃ³n general y con acceso total al sistema.

## ACT-02 â€” Operador de almacÃ©n

Usuario encargado de registrar productos, movimientos e importaciones, segÃºn permisos.

## ACT-03 â€” Usuario de consulta

Usuario con permisos Ãºnicamente para consultar, filtrar, exportar e imprimir informaciÃ³n.

> En una primera versiÃ³n local puede existir Ãºnicamente el perfil Administrador, dejando preparada la estructura para incorporar otros perfiles.

---

# 4. Requerimientos funcionales

## 4.1 AutenticaciÃ³n y usuarios

### RF-001 â€” Inicio de sesiÃ³n

El sistema deberÃ¡ permitir el acceso mediante usuario y contraseÃ±a.

**Criterios de aceptaciÃ³n:**

- Debe impedir el acceso con credenciales invÃ¡lidas.
- Debe permitir cerrar sesiÃ³n.
- La contraseÃ±a no deberÃ¡ almacenarse en texto plano.

### RF-002 â€” GestiÃ³n de usuarios

El administrador podrÃ¡ crear, editar, activar o desactivar usuarios.

### RF-003 â€” Roles y permisos

El sistema deberÃ¡ permitir asociar permisos segÃºn perfil.

---

# 5. GestiÃ³n de productos

### RF-010 â€” Registrar producto

El sistema deberÃ¡ permitir registrar un producto con los siguientes datos mÃ­nimos:

- CÃ³digo.
- Nombre.
- CategorÃ­a.
- Unidad de medida.
- Estado.

Datos opcionales:

- CÃ³digo de barras.
- DescripciÃ³n.
- Marca.
- Proveedor principal.
- Precio de compra.
- Precio de venta.
- Stock mÃ­nimo.
- Stock mÃ¡ximo.
- UbicaciÃ³n.
- Observaciones.

### RF-011 â€” CÃ³digo Ãºnico

El cÃ³digo de producto deberÃ¡ ser Ãºnico.

### RF-012 â€” CÃ³digo de barras Ãºnico

Si se utiliza cÃ³digo de barras, no deberÃ¡ repetirse entre productos activos.

### RF-013 â€” Editar producto

El usuario autorizado podrÃ¡ modificar la informaciÃ³n maestra del producto.

### RF-014 â€” Consultar producto

El sistema deberÃ¡ mostrar el detalle completo del producto.

### RF-015 â€” Desactivar producto

Los productos con historial de movimientos no deberÃ¡n eliminarse fÃ­sicamente. DeberÃ¡n quedar en estado Inactivo.

### RF-016 â€” Reactivar producto

Un usuario autorizado podrÃ¡ reactivar productos previamente desactivados.

---

# 6. Datos maestros

### RF-020 â€” CategorÃ­as

Permitir crear, editar, consultar y desactivar categorÃ­as.

### RF-021 â€” Marcas

Permitir crear, editar, consultar y desactivar marcas.

### RF-022 â€” Unidades de medida

Permitir administrar unidades de medida.

Ejemplos:

- Unidad.
- Caja.
- Paquete.
- Kilogramo.
- Litro.
- Metro.

### RF-023 â€” Proveedores

Permitir administrar proveedores.

### RF-024 â€” Ubicaciones

Permitir definir ubicaciones dentro del almacÃ©n.

Ejemplo:

`Zona A > Estante 03 > Nivel 02 > PosiciÃ³n 04`

---

# 7. Inventario y stock

### RF-030 â€” Consultar stock actual

El sistema deberÃ¡ mostrar el stock actual de cada producto.

### RF-031 â€” No editar stock directamente

El stock no deberÃ¡ modificarse directamente desde la ficha del producto.

Toda variaciÃ³n deberÃ¡ originarse mediante un movimiento de inventario o una importaciÃ³n autorizada que genere trazabilidad.

### RF-032 â€” Evitar stock negativo

Por defecto, el sistema deberÃ¡ impedir movimientos que produzcan stock negativo.

Esta regla podrÃ¡ ser configurable si el negocio lo requiere.

### RF-033 â€” Historial de stock

El usuario deberÃ¡ poder consultar los movimientos histÃ³ricos de un producto.

---

# 8. Movimientos de inventario

### RF-040 â€” Entrada de inventario

Permitir registrar entradas indicando:

- Producto.
- Cantidad.
- Fecha.
- Motivo.
- Usuario.
- Documento de referencia opcional.
- ObservaciÃ³n opcional.

### RF-041 â€” Salida de inventario

Permitir registrar salidas con los mismos datos mÃ­nimos de trazabilidad.

### RF-042 â€” Ajuste de inventario

Permitir registrar ajustes positivos o negativos.

Todo ajuste deberÃ¡ requerir un motivo.

### RF-043 â€” Tipos de movimiento

El sistema deberÃ¡ permitir definir tipos de movimiento, por ejemplo:

- Compra.
- DevoluciÃ³n.
- Ingreso inicial.
- Venta.
- Consumo.
- Entrega.
- PÃ©rdida.
- Ajuste de inventario.

### RF-044 â€” Trazabilidad del movimiento

Todo movimiento deberÃ¡ registrar:

- Stock anterior.
- Cantidad modificada.
- Stock resultante.
- Usuario.
- Fecha y hora.
- Tipo de movimiento.

---

# 9. ImportaciÃ³n CSV

### RF-050 â€” SelecciÃ³n de archivo

El usuario podrÃ¡ seleccionar un archivo CSV desde su equipo.

### RF-051 â€” ValidaciÃ³n de estructura

Antes de importar, el sistema deberÃ¡ validar:

- Columnas obligatorias.
- Formato del archivo.
- Tipos de datos.
- Duplicados.
- Campos vacÃ­os obligatorios.
- CÃ³digos invÃ¡lidos.
- Cantidades invÃ¡lidas.
- Fechas invÃ¡lidas.

### RF-052 â€” Vista previa

El sistema deberÃ¡ mostrar una vista previa antes de aplicar cambios.

La vista deberÃ¡ resumir:

- Total de registros.
- Registros nuevos.
- Registros a actualizar.
- Registros con error.

### RF-053 â€” Modo de importaciÃ³n

El usuario autorizado podrÃ¡ elegir entre:

- Solo insertar nuevos registros.
- Solo actualizar existentes.
- Insertar y actualizar.

### RF-054 â€” Identificador de actualizaciÃ³n

El cÃ³digo de producto serÃ¡ el identificador principal para reconocer un producto existente, salvo que el negocio defina otro campo.

### RF-055 â€” ConfirmaciÃ³n

El sistema no deberÃ¡ aplicar cambios hasta que el usuario confirme la importaciÃ³n.

### RF-056 â€” ImportaciÃ³n transaccional

Cuando sea tÃ©cnicamente posible, la importaciÃ³n deberÃ¡ ejecutarse de forma transaccional para evitar estados inconsistentes.

### RF-057 â€” Informe de errores

El sistema deberÃ¡ permitir exportar los errores encontrados.

### RF-058 â€” Historial de importaciones

Cada importaciÃ³n deberÃ¡ registrar:

- Nombre del archivo.
- Fecha y hora.
- Usuario.
- Total de registros.
- Insertados.
- Actualizados.
- Rechazados.
- Estado del proceso.

---

# 10. BÃºsquedas y filtros

### RF-060 â€” BÃºsqueda rÃ¡pida

Permitir buscar por:

- CÃ³digo.
- Nombre.
- CÃ³digo de barras.

### RF-061 â€” Filtros avanzados

Permitir filtrar por:

- CategorÃ­a.
- Marca.
- Proveedor.
- UbicaciÃ³n.
- Estado.
- Stock igual a cero.
- Stock menor al mÃ­nimo.
- Stock mayor al mÃ¡ximo.
- Rango de precios.
- Fecha de registro.

### RF-062 â€” CombinaciÃ³n de filtros

Los filtros deberÃ¡n poder combinarse.

### RF-063 â€” Limpiar filtros

El usuario deberÃ¡ poder restablecer rÃ¡pidamente la bÃºsqueda.

---

# 11. Alertas

### RF-070 â€” Stock mÃ­nimo

Generar alerta cuando el stock actual sea menor o igual al stock mÃ­nimo configurado.

### RF-071 â€” Sin stock

Generar alerta para productos con stock igual a cero.

### RF-072 â€” Stock mÃ¡ximo

Opcionalmente generar alerta cuando el stock supere el mÃ¡ximo configurado.

### RF-073 â€” VisualizaciÃ³n de alertas

Las alertas deberÃ¡n mostrarse en el Dashboard y permitir navegar al listado correspondiente.

### RF-074 â€” Vencimientos

Si el negocio activa gestiÃ³n por lotes o vencimientos, el sistema deberÃ¡ permitir alertas de productos prÃ³ximos a vencer y vencidos.

---

# 12. Dashboard

### RF-080 â€” Indicadores generales

Mostrar al menos:

- Total de productos.
- Productos activos.
- Productos sin stock.
- Productos por debajo del stock mÃ­nimo.
- Entradas del dÃ­a.
- Salidas del dÃ­a.
- Valor estimado del inventario, si se administran costos.

### RF-081 â€” Accesos rÃ¡pidos

El Dashboard deberÃ¡ permitir acceder directamente a las alertas y funcionalidades principales.

---

# 13. Reportes y exportaciÃ³n

### RF-090 â€” Exportar CSV

Permitir exportar listados completos o filtrados a CSV.

### RF-091 â€” Exportar Excel

Permitir exportar listados completos o filtrados a XLSX.

### RF-092 â€” Exportar PDF

Permitir generar reportes PDF preparados para presentaciÃ³n o impresiÃ³n.

### RF-093 â€” Reportes mÃ­nimos

- Inventario general.
- Stock bajo.
- Productos sin stock.
- Inventario por categorÃ­a.
- Movimientos por perÃ­odo.
- Historial de producto.
- Inventario valorizado, si aplica.

### RF-094 â€” Filtros en reportes

Los reportes deberÃ¡n permitir seleccionar criterios antes de generar el archivo.

### RF-095 â€” Vista previa de impresiÃ³n

El usuario podrÃ¡ visualizar el reporte antes de imprimir.

---

# 14. AuditorÃ­a

### RF-100 â€” Registrar acciones relevantes

Registrar como mÃ­nimo:

- CreaciÃ³n de producto.
- ModificaciÃ³n de producto.
- DesactivaciÃ³n/reactivaciÃ³n.
- Entrada.
- Salida.
- Ajuste.
- ImportaciÃ³n.
- Cambio de configuraciÃ³n relevante.

### RF-101 â€” InformaciÃ³n auditada

La auditorÃ­a deberÃ¡ almacenar:

- Usuario.
- AcciÃ³n.
- Fecha y hora.
- Entidad afectada.
- Identificador del registro.
- Valor anterior cuando aplique.
- Valor nuevo cuando aplique.

### RF-102 â€” AuditorÃ­a no editable

Los registros de auditorÃ­a no deberÃ¡n ser modificables desde la interfaz comÃºn.

---

# 15. Backup y recuperaciÃ³n

### RF-110 â€” Crear respaldo

El administrador podrÃ¡ generar manualmente una copia de seguridad.

### RF-111 â€” Restaurar respaldo

El administrador podrÃ¡ restaurar una copia vÃ¡lida.

### RF-112 â€” ConfirmaciÃ³n de restauraciÃ³n

Antes de restaurar se deberÃ¡ advertir que la operaciÃ³n reemplazarÃ¡ la informaciÃ³n actual.

### RF-113 â€” Backup automÃ¡tico

Se dejarÃ¡ preparado como mejora futura la posibilidad de realizar respaldos automÃ¡ticos diarios.

---

# 16. ConfiguraciÃ³n

### RF-120 â€” Datos de empresa

Permitir configurar:

- Nombre de empresa.
- RUC opcional.
- Logo.
- DirecciÃ³n.
- TelÃ©fono.
- Datos que aparecerÃ¡n en reportes.

### RF-121 â€” ParÃ¡metros de inventario

Permitir configurar:

- Uso de stock negativo.
- Uso de stock mÃ¡ximo.
- GestiÃ³n de precios.
- GestiÃ³n de vencimientos.
- GestiÃ³n de lotes.

---

# 17. Reglas de negocio

### RN-001

El cÃ³digo de producto deberÃ¡ ser Ãºnico.

### RN-002

Un producto con movimientos histÃ³ricos no podrÃ¡ eliminarse fÃ­sicamente.

### RN-003

Toda modificaciÃ³n de stock deberÃ¡ quedar asociada a una operaciÃ³n trazable.

### RN-004

Los ajustes de stock deberÃ¡n tener motivo obligatorio.

### RN-005

Las importaciones deberÃ¡n validarse antes de confirmar los cambios.

### RN-006

Una fila invÃ¡lida de CSV no deberÃ¡ provocar que el sistema registre datos inconsistentes.

### RN-007

Un producto inactivo no podrÃ¡ utilizarse en nuevos movimientos salvo reactivaciÃ³n.

### RN-008

Los reportes deberÃ¡n reflejar el estado de los datos al momento de su generaciÃ³n.

### RN-009

Las credenciales no deberÃ¡n almacenarse en texto plano.

### RN-010

El sistema deberÃ¡ conservar el historial de movimientos y auditorÃ­a aunque un producto sea desactivado.

---

# 18. Requerimientos no funcionales

### RNF-001 â€” Plataforma

El sistema deberÃ¡ ejecutarse en Windows 10 y Windows 11, salvo definiciÃ³n distinta del cliente.

### RNF-002 â€” OperaciÃ³n offline

Las funciones principales deberÃ¡n trabajar sin conexiÃ³n a Internet.

### RNF-003 â€” Persistencia local

Para el escenario local se recomienda una base de datos embebida, por ejemplo SQLite.

### RNF-004 â€” Rendimiento

Las bÃºsquedas normales deberÃ¡n responder en tiempos adecuados para una operaciÃ³n de escritorio.

Objetivo inicial:

- Consultas simples: menos de 2 segundos en condiciones normales.
- Importaciones: mostrar progreso cuando el volumen sea elevado.

### RNF-005 â€” Integridad

Las operaciones crÃ­ticas deberÃ¡n usar transacciones.

### RNF-006 â€” Usabilidad

La interfaz deberÃ¡ estar orientada a usuarios no tÃ©cnicos.

### RNF-007 â€” RecuperaciÃ³n

El sistema deberÃ¡ permitir recuperar la informaciÃ³n mediante un backup vÃ¡lido.

### RNF-008 â€” Seguridad local

La aplicaciÃ³n deberÃ¡:

- proteger contraseÃ±as;
- limitar funcionalidades por rol;
- registrar acciones relevantes;
- evitar alteraciones directas de datos desde la interfaz.

### RNF-009 â€” Escalabilidad lÃ³gica

Aunque esta versiÃ³n sea local, la estructura deberÃ¡ evitar acoplamientos innecesarios para facilitar una futura migraciÃ³n a arquitectura multiusuario.

---

# 19. Modelo de datos preliminar

Entidades iniciales:

- Usuario.
- Rol.
- Permiso.
- Producto.
- CategorÃ­a.
- Marca.
- UnidadMedida.
- Proveedor.
- Ubicacion.
- Inventario.
- Movimiento.
- DetalleMovimiento.
- TipoMovimiento.
- Importacion.
- DetalleImportacion.
- Alerta.
- Auditoria.
- Configuracion.

Entidades opcionales:

- Lote.
- SerieProducto.
- Vencimiento.

---

# 20. Casos de uso principales

## CU-001 â€” Registrar producto

**Actor:** Administrador / Operador.  
**PrecondiciÃ³n:** usuario autenticado con permiso de alta.  
**Flujo principal:**

1. El usuario abre Productos.
2. Selecciona Nuevo.
3. Ingresa los datos.
4. El sistema valida campos obligatorios y duplicados.
5. El usuario guarda.
6. El sistema registra el producto.
7. El sistema registra auditorÃ­a.

**Resultado:** producto creado correctamente.

## CU-002 â€” Registrar salida de inventario

1. Seleccionar producto.
2. Indicar cantidad.
3. Seleccionar tipo/motivo.
4. Validar stock disponible.
5. Confirmar.
6. Registrar movimiento.
7. Actualizar stock.
8. Registrar auditorÃ­a.

## CU-003 â€” Importar CSV

1. Seleccionar archivo.
2. Validar estructura.
3. Validar registros.
4. Mostrar vista previa.
5. Mostrar errores.
6. Seleccionar modo de importaciÃ³n.
7. Confirmar.
8. Aplicar cambios.
9. Registrar historial de importaciÃ³n.
10. Mostrar resumen final.

## CU-004 â€” Generar reporte

1. Seleccionar reporte.
2. Definir filtros.
3. Generar vista previa.
4. Exportar a Excel/PDF o imprimir.

---

# 21. Criterios de aceptaciÃ³n globales del MVP

El MVP serÃ¡ considerado funcional cuando:

- Se pueda registrar y mantener productos.
- Se pueda consultar stock actual.
- Toda entrada, salida y ajuste genere trazabilidad.
- Sea posible importar CSV con validaciÃ³n previa.
- Sea posible actualizar productos existentes desde CSV.
- Se detecten y reporten filas invÃ¡lidas.
- Se puedan realizar bÃºsquedas y filtros combinados.
- Se muestren alertas de stock.
- Se puedan exportar reportes a Excel y PDF.
- Sea posible realizar backup y restauraciÃ³n.
- Las operaciones relevantes queden auditadas.

---

# 22. Riesgos del escenario local

- PÃ©rdida del equipo donde reside la informaciÃ³n.
- Falta de respaldo externo.
- Acceso simultÃ¡neo muy limitado.
- Dificultad para compartir informaciÃ³n en tiempo real.
- Dependencia del usuario para ejecutar backups si no se automatizan.

Mitigaciones recomendadas:

- Backup automÃ¡tico o recordatorio de backup.
- Copia externa en una ubicaciÃ³n segura.
- ExportaciÃ³n periÃ³dica de datos.
- Mantener separaciÃ³n lÃ³gica entre interfaz, negocio y persistencia para facilitar futura migraciÃ³n.

---

# 23. Decisiones pendientes

Antes de cerrar el anÃ¡lisis deberÃ¡n confirmarse:

1. Tipo de productos manejados.
2. Campos exactos del CSV.
3. Identificador Ãºnico real del producto.
4. Si el CSV puede crear nuevos productos.
5. Si se administrarÃ¡n precios.
6. Si se manejarÃ¡n lotes.
7. Si se manejarÃ¡n fechas de vencimiento.
8. Si se manejarÃ¡n nÃºmeros de serie.
9. Reportes obligatorios del cliente.
10. Perfiles reales de usuario.
11. Volumen estimado de registros.
12. Cantidad de movimientos diarios.
13. UbicaciÃ³n de los backups.
14. Necesidad de lector de cÃ³digo de barras.
15. Necesidad futura de trabajar desde mÃ¡s de una PC.

---

# 24. RecomendaciÃ³n de arquitectura inicial

Para una Ãºnica estaciÃ³n de trabajo:

```text
AplicaciÃ³n de escritorio
        |
        v
Capa de servicios / negocio
        |
        v
Repositorio de datos
        |
        v
Base de datos SQLite
```

Se recomienda mantener las capas desacopladas para que en una futura evoluciÃ³n la base local pueda sustituirse por una API y una base de datos central sin reconstruir toda la aplicaciÃ³n.
