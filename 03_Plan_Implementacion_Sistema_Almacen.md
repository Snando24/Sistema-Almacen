# Plan de ImplementaciÃ³n â€” Sistema de GestiÃ³n de AlmacÃ©n

**VersiÃ³n:** 1.0  
**Fecha:** 2026-10-03  
**Aplicable a:** escenario local y escenario multiusuario.

---

# 1. Objetivo

Definir una ruta de trabajo ordenada para analizar, diseÃ±ar, desarrollar, probar y poner en funcionamiento el sistema de gestiÃ³n de almacÃ©n.

El plan estÃ¡ pensado para evitar comenzar directamente con pantallas y CRUD sin cerrar previamente reglas crÃ­ticas de inventario, importaciÃ³n, trazabilidad y arquitectura.

---

# 2. Principios de implementaciÃ³n

1. Primero cerrar reglas de negocio.
2. DiseÃ±ar el modelo de datos antes de construir formularios.
3. Tratar el stock como resultado de movimientos trazables.
4. No permitir importaciones directas sin validaciÃ³n previa.
5. Incorporar auditorÃ­a desde el inicio.
6. DiseÃ±ar primero el MVP.
7. Dejar lotes, series y vencimientos como mÃ³dulos opcionales si todavÃ­a no estÃ¡n confirmados.
8. Separar interfaz, lÃ³gica de negocio y persistencia.
9. Automatizar pruebas de reglas crÃ­ticas.
10. Preparar una evoluciÃ³n local -> multiusuario si existe posibilidad real de crecimiento.

---

# 3. DecisiÃ³n inicial de arquitectura

Antes de desarrollar se deberÃ¡ responder:

## Alternativa A â€” Local

Elegir cuando:

- Solo se usarÃ¡ en una computadora.
- No se requiere trabajo concurrente.
- La informaciÃ³n puede residir localmente.
- Se busca mÃ¡xima simplicidad operativa.

Arquitectura sugerida:

```text
Desktop UI
   |
Servicios de negocio
   |
Repositorios
   |
SQLite
```

## Alternativa B â€” Multiusuario

Elegir cuando:

- Dos o mÃ¡s personas trabajarÃ¡n simultÃ¡neamente.
- Se requiere una Ãºnica fuente central de informaciÃ³n.
- Se necesita control central de usuarios y permisos.
- Existe posibilidad de crecimiento.

Arquitectura sugerida:

```text
Desktop UI
   |
API
   |
Servicios de negocio
   |
Base de datos central
```

---

# 4. Fase 0 â€” Levantamiento y validaciÃ³n funcional

## Objetivo

Cerrar las decisiones que afectan estructura de datos y lÃ³gica.

## Actividades

- Identificar usuarios reales.
- Identificar flujo actual del almacÃ©n.
- Revisar un CSV real.
- Identificar columnas obligatorias.
- Definir identificador Ãºnico del producto.
- Definir reglas de alta y actualizaciÃ³n por CSV.
- Definir tipos de movimiento.
- Definir reglas para stock negativo.
- Definir stock mÃ­nimo y mÃ¡ximo.
- Confirmar uso de precios.
- Confirmar lotes.
- Confirmar vencimientos.
- Confirmar nÃºmeros de serie.
- Definir reportes obligatorios.
- Definir perfiles y permisos.
- Estimar cantidad de productos.
- Estimar cantidad de movimientos diarios.
- Confirmar escenario local o multiusuario.

## Entregables

- Documento de requerimientos validado.
- Lista de reglas de negocio aprobadas.
- CSV de ejemplo.
- Diccionario preliminar de campos.
- Lista de reportes.
- Matriz de permisos.

## Criterio de salida

No iniciar construcciÃ³n del modelo final hasta resolver las decisiones que cambian el diseÃ±o de inventario.

---

# 5. Fase 1 â€” DiseÃ±o funcional

## Objetivo

Convertir requerimientos en flujos concretos de uso.

## Actividades

DiseÃ±ar:

- Login.
- Dashboard.
- Listado de productos.
- Alta de producto.
- EdiciÃ³n de producto.
- Detalle de producto.
- CategorÃ­as.
- Marcas.
- Unidades.
- Proveedores.
- Ubicaciones.
- Entradas.
- Salidas.
- Ajustes.
- ImportaciÃ³n CSV.
- Vista previa de importaciÃ³n.
- Listado de errores.
- Alertas.
- Reportes.
- ConfiguraciÃ³n.
- AuditorÃ­a.

## Entregables

- Mapa de navegaciÃ³n.
- Wireframes.
- Flujos de usuario.
- Estados de cada pantalla.
- Mensajes de error funcionales.

---

# 6. Fase 2 â€” DiseÃ±o de datos

## Objetivo

Definir un modelo robusto antes de implementar formularios.

## Entidades mÃ­nimas

- Usuario.
- Rol.
- Producto.
- CategorÃ­a.
- Marca.
- UnidadMedida.
- Proveedor.
- Ubicacion.
- Inventario.
- TipoMovimiento.
- Movimiento.
- DetalleMovimiento.
- Importacion.
- DetalleImportacion.
- Auditoria.
- Configuracion.

## Actividades

- Definir claves primarias.
- Definir relaciones.
- Definir restricciones Ãºnicas.
- Definir campos obligatorios.
- Definir Ã­ndices.
- Definir estrategia de estados activos/inactivos.
- Definir estrategia de auditorÃ­a.
- Definir manejo de decimales y cantidades.
- Definir precisiÃ³n monetaria.
- Definir fechas oficiales.

## Consideraciones especiales

### Escenario local

- SQLite.
- Migraciones/versionado de esquema.
- Backup del archivo de base de datos mediante proceso seguro.

### Escenario multiusuario

- PostgreSQL/SQL Server/MySQL segÃºn decisiÃ³n.
- Restricciones de integridad.
- Transacciones.
- Ãndices.
- Concurrencia.
- Estrategia de backup central.

## Entregables

- Modelo entidad-relaciÃ³n.
- Diccionario de datos.
- Scripts/migraciones iniciales.

---

# 7. Fase 3 â€” Base tÃ©cnica del proyecto

## Objetivo

Preparar la estructura antes de comenzar funcionalidades de negocio.

## Actividades comunes

- Crear repositorio Git.
- Definir ramas y convenciÃ³n de commits.
- Configurar proyecto.
- Configurar manejo de errores.
- Configurar logging.
- Configurar acceso a datos.
- Configurar migraciones.
- Configurar pruebas unitarias.
- Configurar variables de entorno o archivo de configuraciÃ³n.

## Local

- Configurar base embebida.
- Crear servicio de backup.

## Multiusuario

- Crear API.
- Configurar autenticaciÃ³n.
- Configurar autorizaciÃ³n.
- Configurar conexiÃ³n a base central.
- Definir contrato cliente/API.

## Entregables

- AplicaciÃ³n iniciando correctamente.
- ConexiÃ³n a base de datos funcional.
- Migraciones ejecutables.
- Proyecto listo para mÃ³dulos funcionales.

---

# 8. Fase 4 â€” Seguridad y usuarios

## Implementar

- Login.
- Logout.
- Hash de contraseÃ±as.
- Usuarios.
- Roles.
- Permisos.
- Usuario activo/inactivo.

## Multiusuario adicional

- Tokens o sesiones.
- ExpiraciÃ³n de sesiÃ³n.
- AutorizaciÃ³n en API.

## Pruebas

- Credenciales vÃ¡lidas.
- Credenciales invÃ¡lidas.
- Usuario desactivado.
- Acceso sin permiso.
- Cambio de contraseÃ±a.

---

# 9. Fase 5 â€” Maestros y productos

## Orden recomendado

1. CategorÃ­as.
2. Marcas.
3. Unidades.
4. Proveedores.
5. Ubicaciones.
6. Productos.

## Funcionalidades

- Crear.
- Editar.
- Consultar.
- Desactivar.
- Reactivar.
- Buscar.
- Filtrar.

## Pruebas importantes

- CÃ³digo duplicado.
- CÃ³digo de barras duplicado.
- Producto inactivo.
- Campos obligatorios.
- Valores numÃ©ricos invÃ¡lidos.

---

# 10. Fase 6 â€” Motor de inventario

## Objetivo

Construir la lÃ³gica mÃ¡s crÃ­tica antes del Dashboard y reportes.

## Implementar

- Inventario inicial.
- Entrada.
- Salida.
- Ajuste.
- Historial.
- Stock anterior.
- Stock resultante.
- Motivos.
- ValidaciÃ³n de stock negativo.

## Regla principal

Nunca actualizar stock sin registrar el movimiento asociado.

## Pruebas obligatorias

- Entrada aumenta stock.
- Salida disminuye stock.
- Ajuste positivo.
- Ajuste negativo.
- Salida mayor al stock disponible.
- Producto inactivo.
- Movimiento de cantidad cero.
- Movimiento con cantidad invÃ¡lida.

## Multiusuario

Agregar pruebas concurrentes:

- Dos salidas simultÃ¡neas.
- Entrada y salida simultÃ¡nea.
- Dos ajustes simultÃ¡neos.

---

# 11. Fase 7 â€” ImportaciÃ³n CSV

## Subfase 7.1 â€” Lectura

- SelecciÃ³n de archivo.
- CodificaciÃ³n.
- Separador.
- Encabezados.

## Subfase 7.2 â€” ValidaciÃ³n

- Columnas requeridas.
- Tipos de datos.
- Duplicados internos.
- CÃ³digos inexistentes.
- CÃ³digos repetidos.
- Cantidades.
- Fechas.

## Subfase 7.3 â€” Vista previa

Mostrar:

- Total.
- Nuevos.
- Actualizables.
- Errores.

## Subfase 7.4 â€” AplicaciÃ³n

Modos:

- Insertar.
- Actualizar.
- Insertar + actualizar.

## Subfase 7.5 â€” Resultado

Mostrar:

- Procesados.
- Insertados.
- Actualizados.
- Rechazados.

## Subfase 7.6 â€” Historial

Guardar resumen de cada importaciÃ³n.

## Pruebas

- CSV vacÃ­o.
- CSV sin encabezado.
- Columna faltante.
- CÃ³digo duplicado.
- Valor numÃ©rico invÃ¡lido.
- Archivo muy grande.
- InterrupciÃ³n durante importaciÃ³n.
- ImportaciÃ³n repetida.

---

# 12. Fase 8 â€” BÃºsquedas, filtros y alertas

## Implementar

- BÃºsqueda por cÃ³digo.
- BÃºsqueda por nombre.
- CÃ³digo de barras.
- CategorÃ­a.
- Proveedor.
- UbicaciÃ³n.
- Estado.
- Stock cero.
- Stock bajo mÃ­nimo.
- Stock sobre mÃ¡ximo.

## Alertas mÃ­nimas

- Sin stock.
- Bajo stock.
- Sobre stock, si aplica.

## Opcionales

- PrÃ³ximo a vencer.
- Vencido.

---

# 13. Fase 9 â€” Dashboard

## Indicadores

- Productos totales.
- Productos activos.
- Sin stock.
- Bajo mÃ­nimo.
- Entradas del dÃ­a.
- Salidas del dÃ­a.
- Valor de inventario.

## Visualizaciones opcionales

- Stock por categorÃ­a.
- Entradas vs. salidas.
- Productos con mayor movimiento.

El Dashboard debe construirse despuÃ©s de que la lÃ³gica de movimientos sea estable.

---

# 14. Fase 10 â€” Reportes y exportaciones

## Implementar

### CSV

- Exportar listado completo.
- Exportar resultado filtrado.

### Excel

- Encabezados.
- Formato numÃ©rico.
- Formato de fechas.
- Auto-filtro.
- Totales cuando corresponda.

### PDF

- Logo.
- Empresa.
- Fecha.
- TÃ­tulo.
- Filtros aplicados.
- NumeraciÃ³n de pÃ¡ginas.

## Reportes iniciales

1. Inventario general.
2. Stock bajo.
3. Sin stock.
4. Productos por categorÃ­a.
5. Movimientos por perÃ­odo.
6. Historial de producto.
7. Inventario valorizado.

---

# 15. Fase 11 â€” AuditorÃ­a

## Auditar

- Productos.
- Movimientos.
- Importaciones.
- Usuarios.
- ConfiguraciÃ³n.

## Validar

- Fecha y hora.
- Usuario.
- AcciÃ³n.
- Registro afectado.
- Valores anteriores y nuevos.

---

# 16. Fase 12 â€” Backup y recuperaciÃ³n

## Local

- BotÃ³n Crear backup.
- SelecciÃ³n de ubicaciÃ³n.
- Validar restauraciÃ³n.
- Advertencia previa.

## Multiusuario

- Backup automÃ¡tico del servidor.
- PolÃ­tica de retenciÃ³n.
- Procedimiento de restauraciÃ³n.
- Prueba periÃ³dica de recuperaciÃ³n.

## Prueba obligatoria

Un backup no debe considerarse vÃ¡lido Ãºnicamente porque se creÃ³; debe probarse al menos una restauraciÃ³n en ambiente de prueba.

---

# 17. Fase 13 â€” Pruebas integrales

## Pruebas funcionales

- CRUD.
- Movimientos.
- ImportaciÃ³n.
- Filtros.
- Alertas.
- Reportes.
- Usuarios.
- AuditorÃ­a.

## Pruebas de integridad

- Operaciones incompletas.
- Fallos durante guardado.
- RepeticiÃ³n de operaciÃ³n.

## Pruebas de rendimiento

- Listado con volumen realista.
- Filtros.
- CSV grande.
- Reportes grandes.

## Multiusuario

- Concurrencia.
- PÃ©rdida de red.
- ReconexiÃ³n.
- Conflictos de ediciÃ³n.

---

# 18. Fase 14 â€” UAT / ValidaciÃ³n con usuario

## Objetivo

Que el usuario real valide los procesos antes de producciÃ³n.

## Escenarios mÃ­nimos

- Crear producto.
- Actualizar producto.
- Registrar entrada.
- Registrar salida.
- Realizar ajuste.
- Importar CSV real.
- Resolver errores de CSV.
- Consultar stock.
- Generar reporte.
- Exportar Excel.
- Generar PDF.
- Revisar alerta.

## Entregable

Acta o documento de conformidad funcional.

---

# 19. Fase 15 â€” Puesta en producciÃ³n

## Local

- Instalar aplicaciÃ³n.
- Crear base de datos inicial.
- Crear usuario administrador.
- Configurar carpeta de backups.
- Importar datos iniciales.
- Validar impresiÃ³n.

## Multiusuario

- Preparar servidor.
- Configurar base de datos.
- Desplegar API.
- Configurar backup.
- Configurar certificados/red.
- Instalar clientes.
- Crear usuarios.
- Importar datos iniciales.

---

# 20. Fase 16 â€” Soporte inicial y estabilizaciÃ³n

Durante las primeras entregas se deberÃ¡ registrar:

- Errores funcionales.
- Mejoras de usabilidad.
- Campos adicionales solicitados.
- Nuevos filtros.
- Nuevos reportes.

Evitar incorporar funcionalidades grandes sin evaluar su impacto en modelo de datos y reglas de negocio.

---

# 21. PriorizaciÃ³n sugerida

## Prioridad P0 â€” CrÃ­tica

- Usuarios/autenticaciÃ³n.
- Productos.
- Inventario.
- Entradas.
- Salidas.
- Ajustes.
- ImportaciÃ³n CSV.
- Integridad de datos.

## Prioridad P1 â€” Alta

- BÃºsquedas.
- Filtros.
- Alertas.
- Excel.
- PDF.
- AuditorÃ­a.
- Backup.

## Prioridad P2 â€” Media

- Dashboard avanzado.
- GrÃ¡ficos.
- Filtros guardados.
- PersonalizaciÃ³n de reportes.

## Prioridad P3 â€” Evolutiva

- Lotes.
- Vencimientos.
- Series.
- MÃºltiples almacenes.
- Transferencias.
- CÃ³digo de barras.
- AplicaciÃ³n web.
- AplicaciÃ³n mÃ³vil.

---

# 22. Backlog inicial sugerido

## Ã‰pica 1 â€” Seguridad

- Login.
- Usuarios.
- Roles.
- Permisos.

## Ã‰pica 2 â€” CatÃ¡logos

- CategorÃ­as.
- Marcas.
- Unidades.
- Proveedores.
- Ubicaciones.

## Ã‰pica 3 â€” Productos

- Alta.
- EdiciÃ³n.
- Consulta.
- DesactivaciÃ³n.
- Filtros.

## Ã‰pica 4 â€” Inventario

- Stock.
- Entradas.
- Salidas.
- Ajustes.
- Historial.

## Ã‰pica 5 â€” Importaciones

- Lectura CSV.
- ValidaciÃ³n.
- Preview.
- AplicaciÃ³n.
- Errores.
- Historial.

## Ã‰pica 6 â€” Alertas

- Sin stock.
- Stock mÃ­nimo.
- Stock mÃ¡ximo.

## Ã‰pica 7 â€” Reportes

- Excel.
- PDF.
- ImpresiÃ³n.

## Ã‰pica 8 â€” AdministraciÃ³n

- AuditorÃ­a.
- ConfiguraciÃ³n.
- Backup.

---

# 23. Orden recomendado para desarrollar

```text
1. Requerimientos
2. DiseÃ±o de datos
3. Base tÃ©cnica
4. Usuarios
5. CatÃ¡logos
6. Productos
7. Inventario
8. Movimientos
9. ImportaciÃ³n CSV
10. Filtros
11. Alertas
12. Dashboard
13. Excel/PDF
14. AuditorÃ­a
15. Backup
16. Pruebas integrales
17. UAT
18. ProducciÃ³n
```

---

# 24. Entregas recomendadas

## Entrega 1 â€” NÃºcleo

- Login.
- CatÃ¡logos.
- Productos.

## Entrega 2 â€” Inventario

- Entradas.
- Salidas.
- Ajustes.
- Historial.

## Entrega 3 â€” Datos masivos

- CSV.
- ValidaciÃ³n.
- Preview.
- Historial de importaciÃ³n.

## Entrega 4 â€” OperaciÃ³n diaria

- Filtros.
- Alertas.
- Dashboard.

## Entrega 5 â€” GestiÃ³n

- Excel.
- PDF.
- Reportes.
- AuditorÃ­a.

## Entrega 6 â€” Cierre MVP

- Backup.
- Pruebas.
- UAT.
- InstalaciÃ³n/despliegue.

---

# 25. DefiniciÃ³n de terminado â€” Definition of Done

Una funcionalidad se considerarÃ¡ terminada cuando:

- Cumpla el requerimiento.
- Cumpla sus reglas de negocio.
- Tenga validaciones.
- Tenga manejo de errores.
- Tenga pruebas funcionales.
- Tenga pruebas unitarias para reglas crÃ­ticas.
- Registre auditorÃ­a cuando corresponda.
- No rompa otras funcionalidades.
- Haya sido revisada en entorno de prueba.

---

# 26. RecomendaciÃ³n para el proyecto

Si existe una posibilidad razonable de que el sistema sea utilizado por varias computadoras en el corto o mediano plazo, conviene desarrollar desde el inicio con separaciÃ³n estricta de capas y evitar que la interfaz manipule directamente la base de datos.

Incluso en el escenario local se recomienda esta estructura:

```text
UI
 |
AplicaciÃ³n / casos de uso
 |
Dominio / reglas
 |
Repositorio
 |
SQLite
```

AsÃ­, una futura evoluciÃ³n podrÃ­a convertirse en:

```text
UI
 |
API
 |
AplicaciÃ³n / casos de uso
 |
Dominio / reglas
 |
Repositorio
 |
PostgreSQL / SQL Server
```

sin reconstruir toda la lÃ³gica del sistema.
