-- SisAlmacen - Datos semilla. Ejecutar después de 001_schema.sql.
-- El usuario administrador NO se siembra aquí: se crea en el primer arranque (asistente) con hash Argon2id.

INSERT INTO rol (codigo, nombre, descripcion, es_sistema) VALUES
 ('ADMIN',    'Administrador',      'Acceso total',                                  1),
 ('OPERADOR', 'Operador de almacén','Productos, entradas, salidas e importaciones',  1),
 ('CONSULTA', 'Usuario de consulta','Solo lectura, reportes y exportación',          1);

INSERT INTO permiso (codigo, descripcion) VALUES
 ('usuarios.gestionar',     'Crear, editar y desactivar usuarios y roles'),
 ('catalogos.ver',          'Ver catálogos'),
 ('catalogos.gestionar',    'Crear, editar y desactivar catálogos'),
 ('productos.ver',          'Ver productos'),
 ('productos.ver_precios',  'Ver precios de compra y venta'),
 ('productos.crear',        'Crear productos'),
 ('productos.editar',       'Editar productos'),
 ('productos.desactivar',   'Desactivar y reactivar productos'),
 ('inventario.ver',         'Ver stock e historial de movimientos'),
 ('movimientos.entrada',    'Registrar entradas'),
 ('movimientos.salida',     'Registrar salidas'),
 ('movimientos.ajuste',     'Registrar ajustes y correcciones'),
 ('importacion.ejecutar',   'Importar CSV'),
 ('importacion.historial',  'Ver historial de importaciones'),
 ('reportes.ver',           'Ver reportes'),
 ('exportar.datos',         'Exportar a CSV, Excel y PDF'),
 ('auditoria.ver',          'Ver auditoría'),
 ('configuracion.gestionar','Modificar configuración'),
 ('backup.gestionar',       'Crear y restaurar respaldos');

INSERT INTO rol_permiso (rol_id, permiso_id)
SELECT r.id, p.id FROM rol r CROSS JOIN permiso p WHERE r.codigo = 'ADMIN';

INSERT INTO rol_permiso (rol_id, permiso_id)
SELECT r.id, p.id FROM rol r JOIN permiso p ON p.codigo IN (
 'catalogos.ver','productos.ver','productos.ver_precios','productos.crear','productos.editar',
 'inventario.ver','movimientos.entrada','movimientos.salida',
 'importacion.ejecutar','importacion.historial','reportes.ver','exportar.datos')
WHERE r.codigo = 'OPERADOR';

INSERT INTO rol_permiso (rol_id, permiso_id)
SELECT r.id, p.id FROM rol r JOIN permiso p ON p.codigo IN (
 'catalogos.ver','productos.ver','inventario.ver','reportes.ver','exportar.datos')
WHERE r.codigo = 'CONSULTA';

INSERT INTO unidad_medida (codigo, nombre, permite_decimales) VALUES
 ('UND','Unidad',0), ('CAJ','Caja',0), ('PAQ','Paquete',0),
 ('KG','Kilogramo',1), ('LT','Litro',1), ('MT','Metro',1);

-- Categorías funcionales iniciales de R&R. Son editables desde Catálogos;
-- no derivan de los colores del archivo Excel histórico.
INSERT INTO categoria (nombre) VALUES
 ('SOLDADURA CORTE Y GASES'),
 ('ABRASIVOS CORTE Y DESBASTE'),
 ('ACEROS Y MATERIALES'),
 ('FERRETERIA Y FIJACIONES'),
 ('REPARACION DE NEUMATICOS'),
 ('ELECTRICIDAD E ILUMINACION'),
 ('PINTURAS ADHESIVOS Y QUIMICOS'),
 ('FRENOS Y SUSPENSION'),
 ('REPUESTOS DE MAQUINARIA PESADA'),
 ('NEUMATICA Y LUBRICACION'),
 ('MAQUINARIA Y EQUIPOS DE TALLER'),
 ('HERRAMIENTAS ELECTRICAS Y NEUMATICAS'),
 ('HERRAMIENTAS MANUALES'),
 ('IZAJE Y ELEVACION'),
 ('EPP Y SEGURIDAD'),
 ('OFICINA Y PAPELERIA'),
 ('INFORMATICA E IMPRESION');

-- naturaleza: define el signo del detalle (ENTRADA/AJUSTE_POS = +1, SALIDA/AJUSTE_NEG = -1).
INSERT INTO tipo_movimiento (codigo, nombre, naturaleza, requiere_motivo, es_sistema) VALUES
 ('ENT_INICIAL',    'Ingreso inicial',            'ENTRADA',    0, 1),
 ('ENT_COMPRA',     'Compra',                     'ENTRADA',    0, 0),
 ('ENT_DEVOLUCION', 'Devolución',                 'ENTRADA',    0, 0),
 ('SAL_VENTA',      'Venta',                      'SALIDA',     0, 0),
 ('SAL_CONSUMO',    'Consumo',                    'SALIDA',     0, 0),
 ('SAL_ENTREGA',    'Entrega',                    'SALIDA',     0, 0),
 ('SAL_PERDIDA',    'Pérdida',                    'SALIDA',     1, 0),
 ('AJ_POSITIVO',    'Ajuste positivo',            'AJUSTE_POS', 1, 1),
 ('AJ_NEGATIVO',    'Ajuste negativo',            'AJUSTE_NEG', 1, 1);

INSERT INTO configuracion (clave, valor, descripcion) VALUES
 ('empresa.nombre',                '',      'Nombre de la empresa en reportes'),
 ('empresa.documento',             '',      'RUC u otro documento (opcional)'),
 ('empresa.direccion',             '',      'Dirección'),
 ('empresa.telefono',              '',      'Teléfono'),
 ('empresa.logo_ruta',             '',      'Ruta del logo'),
 ('moneda.codigo',                 'PEN',   'Moneda (supuesto por RUC; validar)'),
 ('inventario.permitir_stock_negativo', '0','1 = permite stock negativo'),
 ('inventario.usar_stock_maximo',  '0',     'Reservado; el stock máximo no se usa actualmente'),
 ('inventario.usar_precios',       '1',     'Habilita campos de precio y valorización'),
 ('inventario.usar_lotes',         '0',     'Reservado, fuera del MVP'),
 ('inventario.usar_vencimientos',  '0',     'Reservado, fuera del MVP'),
 ('seguridad.max_intentos',        '5',     'Intentos fallidos antes de bloquear'),
 ('seguridad.bloqueo_minutos',     '15',    'Minutos de bloqueo'),
 ('seguridad.password_min_longitud','8',    'Longitud mínima de contraseña'),
 ('importacion.max_filas',         '50000', 'Máximo de filas por CSV'),
 ('backup.carpeta',                '',      'Carpeta por defecto de respaldos'),
 ('backup.recordatorio_dias',      '7',     'Días sin respaldo para recordar'),
 ('ui.tema',                       'claro', 'Tema visual: claro u oscuro');
