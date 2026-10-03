# Documento de Requerimientos â€” Sistema de GestiÃ³n de AlmacÃ©n

## Escenario B: AplicaciÃ³n de escritorio multiusuario / arquitectura cliente-servidor

**VersiÃ³n:** 1.0  
**Estado:** Borrador funcional para validaciÃ³n  
**Fecha:** 2026-10-03  
**Objetivo del documento:** definir el alcance funcional y tÃ©cnico preliminar de una soluciÃ³n de gestiÃ³n de almacÃ©n utilizada simultÃ¡neamente desde varias computadoras, con servidor central, API y base de datos compartida.

---

# 1. Objetivo del sistema

Desarrollar una soluciÃ³n de gestiÃ³n de almacÃ©n que permita a mÃºltiples usuarios trabajar concurrentemente sobre una fuente Ãºnica de informaciÃ³n, controlando productos, stock, movimientos, importaciones, alertas, reportes, auditorÃ­a y permisos.

La soluciÃ³n deberÃ¡ asegurar consistencia de inventario, trazabilidad y control de concurrencia.

---

# 2. Arquitectura conceptual

```text
PC AlmacÃ©n 1 ----\
PC AlmacÃ©n 2 -----\
PC AdministraciÃ³n ---> API / Servidor de AplicaciÃ³n ---> Base de Datos Central
PC Consulta -------/                |
                                   +--> Reportes / archivos
```

Arquitectura recomendada:

- Cliente de escritorio.
- API central.
- Servicios de negocio centralizados.
- Base de datos relacional central.
- Mecanismo de autenticaciÃ³n.
- Control de roles y permisos.
- AuditorÃ­a centralizada.
- Backup del servidor.

TecnologÃ­as posibles, sujetas a decisiÃ³n posterior:

- PostgreSQL.
- SQL Server.
- MySQL/MariaDB.

---

# 3. Alcance del MVP

Incluye:

- Inicio de sesiÃ³n centralizado.
- GestiÃ³n de usuarios.
- Roles y permisos.
- GestiÃ³n de productos.
- CategorÃ­as.
- Marcas.
- Unidades.
- Proveedores.
- Ubicaciones.
- Inventario centralizado.
- Entradas.
- Salidas.
- Ajustes.
- ImportaciÃ³n CSV.
- Historial de importaciones.
- BÃºsqueda y filtros.
- Alertas.
- ExportaciÃ³n Excel.
- ExportaciÃ³n PDF.
- Reportes.
- AuditorÃ­a central.
- Control de concurrencia.
- Copias de seguridad del servidor.
- GestiÃ³n bÃ¡sica de sesiones.

---

# 4. Actores

## ACT-01 â€” Administrador

Gestiona usuarios, permisos, catÃ¡logos, configuraciones y auditorÃ­a.

## ACT-02 â€” Operador de almacÃ©n

Gestiona productos y movimientos segÃºn permisos asignados.

## ACT-03 â€” Supervisor

Consulta inventario, movimientos, alertas y reportes; puede autorizar determinados ajustes si el negocio lo requiere.

## ACT-04 â€” Usuario de consulta

Acceso de solo lectura y generaciÃ³n de reportes.

---

# 5. Requerimientos funcionales base

Los requerimientos funcionales del escenario local se mantienen para:

- Productos.
- CatÃ¡logos.
- Inventario.
- Movimientos.
- ImportaciÃ³n CSV.
- Alertas.
- Dashboard.
- Reportes.
- Exportaciones.
- AuditorÃ­a.

A ellos se aÃ±aden los siguientes requerimientos especÃ­ficos del escenario multiusuario.

---

# 6. AutenticaciÃ³n centralizada

### RF-M001 â€” Inicio de sesiÃ³n central

Los usuarios deberÃ¡n autenticarse contra el servidor.

### RF-M002 â€” SesiÃ³n de usuario

El sistema deberÃ¡ mantener una sesiÃ³n vÃ¡lida mientras el usuario utilice la aplicaciÃ³n.

### RF-M003 â€” ExpiraciÃ³n de sesiÃ³n

La sesiÃ³n podrÃ¡ expirar despuÃ©s de un perÃ­odo configurable de inactividad.

### RF-M004 â€” Bloqueo de usuario

El administrador podrÃ¡ desactivar temporalmente cuentas.

### RF-M005 â€” Cambio de contraseÃ±a

El usuario podrÃ¡ cambiar su contraseÃ±a.

---

# 7. Roles y permisos

### RF-M010 â€” Permisos por funcionalidad

Los permisos deberÃ¡n controlarse desde el servidor.

Ejemplos:

- Ver productos.
- Crear productos.
- Editar productos.
- Desactivar productos.
- Registrar entradas.
- Registrar salidas.
- Registrar ajustes.
- Importar CSV.
- Exportar informaciÃ³n.
- Ver auditorÃ­a.
- Administrar usuarios.

### RF-M011 â€” VerificaciÃ³n en servidor

Los permisos no deberÃ¡n depender Ãºnicamente de ocultar botones en la interfaz. La API deberÃ¡ validar autorizaciones.

---

# 8. Concurrencia

### RF-M020 â€” Consistencia de stock

El sistema deberÃ¡ impedir que dos operaciones simultÃ¡neas generen stock inconsistente.

### RF-M021 â€” ActualizaciÃ³n concurrente

Si dos usuarios modifican el mismo registro, el sistema deberÃ¡ detectar el conflicto y evitar sobreescribir cambios silenciosamente.

### RF-M022 â€” Transacciones de inventario

Los movimientos deberÃ¡n confirmarse de forma atÃ³mica.

Ejemplo:

- Registrar movimiento.
- Actualizar stock.
- Registrar auditorÃ­a.

Todo deberÃ¡ completarse o revertirse como una sola operaciÃ³n lÃ³gica.

### RF-M023 â€” Reserva transitoria de operaciÃ³n

Para operaciones crÃ­ticas podrÃ¡ utilizarse bloqueo lÃ³gico o control optimista segÃºn la arquitectura definida.

---

# 9. Productos

### RF-M030 â€” CatÃ¡logo central

Todos los usuarios deberÃ¡n consultar el mismo catÃ¡logo de productos.

### RF-M031 â€” Cambios en tiempo real lÃ³gico

Una modificaciÃ³n confirmada deberÃ¡ estar disponible para otros usuarios en la siguiente consulta o refresco de informaciÃ³n.

### RF-M032 â€” DesactivaciÃ³n segura

Un producto desactivado no deberÃ¡ estar disponible para nuevos movimientos.

---

# 10. Inventario centralizado

### RF-M040 â€” Fuente Ãºnica de stock

El stock oficial deberÃ¡ mantenerse en la base de datos central.

### RF-M041 â€” Consulta actualizada

Las consultas de inventario deberÃ¡n recuperar el estado vigente del servidor.

### RF-M042 â€” Registro de movimiento

Cada movimiento deberÃ¡ contener:

- Producto.
- Cantidad.
- Tipo.
- Motivo.
- Stock anterior.
- Stock resultante.
- Usuario.
- Fecha y hora del servidor.
- EstaciÃ³n/origen cuando aplique.

---

# 11. ImportaciÃ³n CSV multiusuario

### RF-M050 â€” Procesamiento controlado

El procesamiento del CSV deberÃ¡ ejecutarse bajo reglas centrales de negocio.

### RF-M051 â€” ValidaciÃ³n previa

La aplicaciÃ³n cliente podrÃ¡ mostrar la prevalidaciÃ³n, pero la confirmaciÃ³n final deberÃ¡ ser validada por el servidor.

### RF-M052 â€” Conflictos durante importaciÃ³n

Si un producto cambia entre la vista previa y la confirmaciÃ³n, el sistema deberÃ¡ detectar el conflicto o volver a validar el registro.

### RF-M053 â€” Progreso

Para archivos grandes deberÃ¡ mostrarse el progreso de la importaciÃ³n.

### RF-M054 â€” ImportaciÃ³n concurrente

El sistema deberÃ¡ impedir o controlar dos importaciones simultÃ¡neas que puedan afectar los mismos registros.

---

# 12. Alertas centralizadas

### RF-M060 â€” Alertas comunes

Las alertas se calcularÃ¡n a partir del inventario central.

### RF-M061 â€” Alertas por rol

PodrÃ¡ definirse quÃ© perfiles pueden visualizar cada tipo de alerta.

### RF-M062 â€” Refresco

Las alertas deberÃ¡n actualizarse al volver a consultar el Dashboard o mediante un mecanismo de actualizaciÃ³n definido.

---

# 13. AuditorÃ­a multiusuario

### RF-M070 â€” AuditorÃ­a central

Toda operaciÃ³n relevante deberÃ¡ quedar registrada en el servidor.

### RF-M071 â€” Datos de auditorÃ­a

Registrar:

- Usuario.
- Rol.
- Fecha y hora del servidor.
- OperaciÃ³n.
- Entidad.
- Identificador.
- Valores anteriores y nuevos cuando corresponda.
- Origen o estaciÃ³n cliente si se requiere.

### RF-M072 â€” Solo lectura

La auditorÃ­a serÃ¡ de solo lectura para usuarios autorizados.

---

# 14. Reportes y exportaciones

### RF-M080 â€” Datos centralizados

Los reportes deberÃ¡n construirse con informaciÃ³n recuperada del servidor.

### RF-M081 â€” Reportes por permisos

El servidor deberÃ¡ validar que el usuario tenga autorizaciÃ³n para acceder a la informaciÃ³n solicitada.

### RF-M082 â€” Exportaciones

Permitir exportaciÃ³n a:

- CSV.
- Excel.
- PDF.

### RF-M083 â€” ImpresiÃ³n

El archivo o vista generada podrÃ¡ imprimirse desde el equipo cliente.

---

# 15. AdministraciÃ³n del servidor

### RF-M090 â€” Estado del servicio

El sistema deberÃ¡ detectar cuando el servidor no estÃ© disponible.

### RF-M091 â€” Mensaje de indisponibilidad

Ante pÃ©rdida de conexiÃ³n, el cliente deberÃ¡ mostrar un mensaje entendible y evitar que el usuario crea que una operaciÃ³n no confirmada fue registrada.

### RF-M092 â€” Reintento seguro

No deberÃ¡ reenviarse automÃ¡ticamente una operaciÃ³n crÃ­tica si existe riesgo de duplicarla.

---

# 16. Backup y recuperaciÃ³n

### RF-M100 â€” Backup central

El respaldo se realizarÃ¡ sobre la base de datos del servidor.

### RF-M101 â€” AutomatizaciÃ³n

Se recomienda programar backups automÃ¡ticos.

### RF-M102 â€” PolÃ­tica de retenciÃ³n

Definir una polÃ­tica de retenciÃ³n, por ejemplo:

- Diario: Ãºltimos 7 dÃ­as.
- Semanal: Ãºltimas 4 semanas.
- Mensual: Ãºltimos 6 o 12 meses.

### RF-M103 â€” RestauraciÃ³n

La restauraciÃ³n deberÃ¡ ejecutarse por un administrador tÃ©cnico autorizado.

---

# 17. Reglas de negocio

AdemÃ¡s de las reglas del escenario local:

### RN-M001

El servidor serÃ¡ la fuente oficial de informaciÃ³n.

### RN-M002

NingÃºn cliente podrÃ¡ actualizar directamente la base de datos saltÃ¡ndose las reglas de negocio.

### RN-M003

Toda operaciÃ³n de inventario deberÃ¡ validar permisos y stock en el servidor antes de confirmarse.

### RN-M004

La fecha/hora oficial de las transacciones serÃ¡ la del servidor.

### RN-M005

Los conflictos de actualizaciÃ³n deberÃ¡n notificarse al usuario.

### RN-M006

Las importaciones deberÃ¡n volver a validarse al momento de confirmar.

### RN-M007

Los movimientos confirmados no deberÃ¡n eliminarse fÃ­sicamente. Una correcciÃ³n deberÃ¡ realizarse mediante un movimiento compensatorio o mecanismo autorizado.

---

# 18. Requerimientos no funcionales

### RNF-M001 â€” Disponibilidad

La aplicaciÃ³n dependerÃ¡ de la disponibilidad del servidor dentro de la red definida.

### RNF-M002 â€” Seguridad de comunicaciones

Cuando exista comunicaciÃ³n por red, se deberÃ¡ utilizar un canal protegido, especialmente si la aplicaciÃ³n sale de una red local controlada.

### RNF-M003 â€” Rendimiento

Objetivos iniciales:

- Consultas frecuentes: respuesta percibida menor a 2 segundos en condiciones normales.
- Operaciones de inventario: confirmaciÃ³n rÃ¡pida y consistente.
- Importaciones grandes: procesamiento con indicador de progreso.

### RNF-M004 â€” Concurrencia

La soluciÃ³n deberÃ¡ soportar mÃºltiples usuarios simultÃ¡neos segÃºn la volumetrÃ­a acordada.

### RNF-M005 â€” Integridad transaccional

Toda operaciÃ³n crÃ­tica deberÃ¡ utilizar transacciones en servidor.

### RNF-M006 â€” Registro de errores

El servidor deberÃ¡ registrar errores tÃ©cnicos para diagnÃ³stico.

### RNF-M007 â€” Escalabilidad

La arquitectura deberÃ¡ permitir aumentar usuarios y volumen de datos sin reemplazar completamente el sistema.

### RNF-M008 â€” Mantenibilidad

Separar:

- Cliente.
- API.
- LÃ³gica de negocio.
- Persistencia.

### RNF-M009 â€” Seguridad de credenciales

Las contraseÃ±as deberÃ¡n almacenarse usando un mecanismo de hash seguro.

### RNF-M010 â€” Principio de mÃ­nimo privilegio

Cada usuario deberÃ¡ disponer Ãºnicamente de los permisos necesarios.

---

# 19. Modelo de datos preliminar

Entidades principales:

- Usuario.
- Rol.
- Permiso.
- UsuarioRol.
- RolPermiso.
- Producto.
- Categoria.
- Marca.
- UnidadMedida.
- Proveedor.
- Almacen.
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
- Sesion o Token, segÃºn diseÃ±o.

Opcionales:

- Lote.
- SerieProducto.
- Vencimiento.
- Transferencia.
- DetalleTransferencia.

---

# 20. API conceptual

Ejemplos de recursos que podrÃ­an existir:

```text
/auth
/users
/roles
/products
/categories
/brands
/suppliers
/locations
/inventory
/movements
/imports
/alerts
/reports
/audit
/settings
```

La definiciÃ³n final de endpoints deberÃ¡ realizarse durante el diseÃ±o tÃ©cnico.

---

# 21. Casos de uso crÃ­ticos del escenario multiusuario

## CU-M001 â€” Salida concurrente

**SituaciÃ³n:** dos usuarios intentan retirar unidades del mismo producto.

**Resultado esperado:**

- El servidor valida el stock real al momento de cada operaciÃ³n.
- La segunda operaciÃ³n no podrÃ¡ dejar stock negativo si la primera ya consumiÃ³ las unidades disponibles.

## CU-M002 â€” EdiciÃ³n concurrente

**SituaciÃ³n:** dos usuarios editan el mismo producto.

**Resultado esperado:**

- El sistema detecta que el registro fue modificado.
- Se informa el conflicto.
- El usuario decide volver a cargar la informaciÃ³n antes de guardar.

## CU-M003 â€” ImportaciÃ³n mientras existen movimientos

**SituaciÃ³n:** una importaciÃ³n pretende actualizar datos mientras otros usuarios trabajan.

**Resultado esperado:**

- El servidor vuelve a validar cada operaciÃ³n crÃ­tica.
- Se evitan sobrescrituras inconsistentes.

---

# 22. Criterios de aceptaciÃ³n globales

El escenario multiusuario serÃ¡ considerado funcional cuando:

- Dos o mÃ¡s estaciones puedan conectarse al mismo sistema.
- Los usuarios trabajen sobre la misma informaciÃ³n central.
- Los permisos se validen en servidor.
- Dos movimientos simultÃ¡neos no generen stock inconsistente.
- La auditorÃ­a identifique quÃ© usuario realizÃ³ cada operaciÃ³n.
- Las importaciones puedan ejecutarse sin vulnerar consistencia.
- Los reportes reflejen informaciÃ³n centralizada.
- Exista una estrategia de backup del servidor.
- Los clientes reaccionen correctamente ante pÃ©rdida de conexiÃ³n.

---

# 23. Riesgos del escenario multiusuario

- CaÃ­da del servidor.
- Fallo de red.
- Errores de concurrencia.
- Operaciones duplicadas por reintentos incorrectos.
- Permisos mal configurados.
- Mayor complejidad de instalaciÃ³n y soporte.
- Necesidad de monitorear servidor y base de datos.

Mitigaciones:

- Transacciones.
- Restricciones de base de datos.
- Control de concurrencia.
- Backups automÃ¡ticos.
- Logs centralizados.
- ValidaciÃ³n de permisos en API.
- Pruebas concurrentes.
- Procedimiento documentado de recuperaciÃ³n.

---

# 24. Decisiones pendientes

1. Cantidad estimada de usuarios concurrentes.
2. Red local o acceso remoto.
3. Necesidad de acceso fuera de la empresa.
4. Base de datos objetivo.
5. Servidor Windows o Linux.
6. Infraestructura local o nube.
7. Volumen de productos.
8. Volumen de movimientos diarios.
9. TamaÃ±o mÃ¡ximo de CSV.
10. PolÃ­ticas de contraseÃ±a.
11. PolÃ­tica de backup.
12. Necesidad de alta disponibilidad.
13. Necesidad de mÃºltiples almacenes.
14. Necesidad de sincronizaciÃ³n offline.
15. Necesidad futura de aplicaciÃ³n web o mÃ³vil.

---

# 25. RecomendaciÃ³n de arquitectura

Para este escenario se recomienda:

```text
Cliente escritorio
       |
       | HTTPS / red segura
       v
API / Servicios de negocio
       |
       v
Base de datos relacional central
```

El cliente no deberÃ¡ conectarse directamente a la base de datos si se busca una arquitectura mantenible, segura y extensible.
