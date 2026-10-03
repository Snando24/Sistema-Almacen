BEGIN TRANSACTION;
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO "alembic_version" VALUES('0001_initial');
CREATE TABLE auditoria (
    id             INTEGER PRIMARY KEY,
    fecha_hora     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    usuario_id     INTEGER REFERENCES usuario(id),
    username       TEXT,
    accion         TEXT NOT NULL,
    entidad        TEXT NOT NULL,
    entidad_id     TEXT,
    valor_anterior TEXT,                                       -- JSON
    valor_nuevo    TEXT,                                       -- JSON
    detalle        TEXT,
    estacion       TEXT
);
CREATE TABLE categoria (
    id          INTEGER PRIMARY KEY,
    nombre      TEXT NOT NULL COLLATE NOCASE UNIQUE,
    descripcion TEXT,
    activo      INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    row_version INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE configuracion (
    clave        TEXT PRIMARY KEY,
    valor        TEXT NOT NULL,
    descripcion  TEXT,
    actualizado_en TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
INSERT INTO "configuracion" VALUES('empresa.nombre','','Nombre de la empresa en reportes','2026-10-03T14:27:13Z');
INSERT INTO "configuracion" VALUES('empresa.documento','','RUC u otro documento (opcional)','2026-10-03T14:27:13Z');
INSERT INTO "configuracion" VALUES('empresa.direccion','','Dirección','2026-10-03T14:27:13Z');
INSERT INTO "configuracion" VALUES('empresa.telefono','','Teléfono','2026-10-03T14:27:13Z');
INSERT INTO "configuracion" VALUES('empresa.logo_ruta','','Ruta del logo','2026-10-03T14:27:13Z');
INSERT INTO "configuracion" VALUES('moneda.codigo','PEN','Moneda (supuesto por RUC; validar)','2026-10-03T14:27:13Z');
INSERT INTO "configuracion" VALUES('inventario.permitir_stock_negativo','0','1 = permite stock negativo','2026-10-03T14:27:13Z');
INSERT INTO "configuracion" VALUES('inventario.usar_stock_maximo','1','Habilita alerta de sobre stock','2026-10-03T14:27:13Z');
INSERT INTO "configuracion" VALUES('inventario.usar_precios','1','Habilita campos de precio y valorización','2026-10-03T14:27:13Z');
INSERT INTO "configuracion" VALUES('inventario.usar_lotes','0','Reservado, fuera del MVP','2026-10-03T14:27:13Z');
INSERT INTO "configuracion" VALUES('inventario.usar_vencimientos','0','Reservado, fuera del MVP','2026-10-03T14:27:13Z');
INSERT INTO "configuracion" VALUES('seguridad.max_intentos','5','Intentos fallidos antes de bloquear','2026-10-03T14:27:13Z');
INSERT INTO "configuracion" VALUES('seguridad.bloqueo_minutos','15','Minutos de bloqueo','2026-10-03T14:27:13Z');
INSERT INTO "configuracion" VALUES('seguridad.password_min_longitud','8','Longitud mínima de contraseña','2026-10-03T14:27:13Z');
INSERT INTO "configuracion" VALUES('importacion.max_filas','50000','Máximo de filas por CSV','2026-10-03T14:27:13Z');
INSERT INTO "configuracion" VALUES('backup.carpeta','','Carpeta por defecto de respaldos','2026-10-03T14:27:13Z');
INSERT INTO "configuracion" VALUES('backup.recordatorio_dias','7','Días sin respaldo para recordar','2026-10-03T14:27:13Z');
CREATE TABLE detalle_importacion (
    id             INTEGER PRIMARY KEY,
    importacion_id INTEGER NOT NULL REFERENCES importacion(id) ON DELETE CASCADE,
    nro_fila       INTEGER NOT NULL,
    codigo         TEXT,
    accion         TEXT NOT NULL CHECK (accion IN ('INSERTAR','ACTUALIZAR','SIN_CAMBIOS','ERROR')),
    datos_json     TEXT,
    errores_json   TEXT
);
CREATE TABLE detalle_movimiento (
    id               INTEGER PRIMARY KEY,
    movimiento_id    INTEGER NOT NULL REFERENCES movimiento(id),
    producto_id      INTEGER NOT NULL REFERENCES producto(id),
    signo            INTEGER NOT NULL CHECK (signo IN (-1,1)),
    cantidad         INTEGER NOT NULL CHECK (cantidad > 0),
    stock_anterior   INTEGER NOT NULL,
    stock_resultante INTEGER NOT NULL,
    precio_unitario  INTEGER CHECK (precio_unitario IS NULL OR precio_unitario >= 0),
    CHECK (stock_resultante = stock_anterior + signo * cantidad)
);
CREATE TABLE importacion (
    id               INTEGER PRIMARY KEY,
    nombre_archivo   TEXT NOT NULL,
    hash_sha256      TEXT NOT NULL,
    modo             TEXT NOT NULL CHECK (modo IN ('INSERTAR','ACTUALIZAR','INSERTAR_ACTUALIZAR')),
    aplicar_stock    INTEGER NOT NULL DEFAULT 0 CHECK (aplicar_stock IN (0,1)),
    usuario_id       INTEGER NOT NULL REFERENCES usuario(id),
    iniciado_en      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    finalizado_en    TEXT,
    estado           TEXT NOT NULL CHECK (estado IN ('VALIDADA','APLICADA','CANCELADA','FALLIDA')),
    total_filas      INTEGER NOT NULL DEFAULT 0,
    filas_nuevas     INTEGER NOT NULL DEFAULT 0,
    filas_actualizables INTEGER NOT NULL DEFAULT 0,
    filas_error      INTEGER NOT NULL DEFAULT 0,
    insertados       INTEGER NOT NULL DEFAULT 0,
    actualizados     INTEGER NOT NULL DEFAULT 0,
    rechazados       INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE inventario (
    producto_id    INTEGER PRIMARY KEY REFERENCES producto(id),
    cantidad       INTEGER NOT NULL DEFAULT 0,
    actualizado_en TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    row_version    INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE marca (
    id          INTEGER PRIMARY KEY,
    nombre      TEXT NOT NULL COLLATE NOCASE UNIQUE,
    activo      INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    row_version INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE movimiento (
    id                   INTEGER PRIMARY KEY,
    tipo_movimiento_id   INTEGER NOT NULL REFERENCES tipo_movimiento(id),
    fecha_movimiento     TEXT NOT NULL,                       -- fecha del negocio (YYYY-MM-DD)
    creado_en            TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    usuario_id           INTEGER NOT NULL REFERENCES usuario(id),
    motivo               TEXT,
    documento_referencia TEXT,
    observacion          TEXT,
    importacion_id       INTEGER REFERENCES importacion(id),
    movimiento_origen_id INTEGER REFERENCES movimiento(id)    -- corrección compensatoria (RN-M007)
);
CREATE TABLE permiso (
    id          INTEGER PRIMARY KEY,
    codigo      TEXT NOT NULL UNIQUE,
    descripcion TEXT NOT NULL
);
INSERT INTO "permiso" VALUES(1,'usuarios.gestionar','Crear, editar y desactivar usuarios y roles');
INSERT INTO "permiso" VALUES(2,'catalogos.ver','Ver catálogos');
INSERT INTO "permiso" VALUES(3,'catalogos.gestionar','Crear, editar y desactivar catálogos');
INSERT INTO "permiso" VALUES(4,'productos.ver','Ver productos');
INSERT INTO "permiso" VALUES(5,'productos.ver_precios','Ver precios de compra y venta');
INSERT INTO "permiso" VALUES(6,'productos.crear','Crear productos');
INSERT INTO "permiso" VALUES(7,'productos.editar','Editar productos');
INSERT INTO "permiso" VALUES(8,'productos.desactivar','Desactivar y reactivar productos');
INSERT INTO "permiso" VALUES(9,'inventario.ver','Ver stock e historial de movimientos');
INSERT INTO "permiso" VALUES(10,'movimientos.entrada','Registrar entradas');
INSERT INTO "permiso" VALUES(11,'movimientos.salida','Registrar salidas');
INSERT INTO "permiso" VALUES(12,'movimientos.ajuste','Registrar ajustes y correcciones');
INSERT INTO "permiso" VALUES(13,'importacion.ejecutar','Importar CSV');
INSERT INTO "permiso" VALUES(14,'importacion.historial','Ver historial de importaciones');
INSERT INTO "permiso" VALUES(15,'reportes.ver','Ver reportes');
INSERT INTO "permiso" VALUES(16,'exportar.datos','Exportar a CSV, Excel y PDF');
INSERT INTO "permiso" VALUES(17,'auditoria.ver','Ver auditoría');
INSERT INTO "permiso" VALUES(18,'configuracion.gestionar','Modificar configuración');
INSERT INTO "permiso" VALUES(19,'backup.gestionar','Crear y restaurar respaldos');
CREATE TABLE producto (
    id             INTEGER PRIMARY KEY,
    codigo         TEXT NOT NULL COLLATE NOCASE UNIQUE,
    codigo_barras  TEXT,
    nombre         TEXT NOT NULL,
    descripcion    TEXT,
    categoria_id   INTEGER NOT NULL REFERENCES categoria(id),
    unidad_id      INTEGER NOT NULL REFERENCES unidad_medida(id),
    marca_id       INTEGER REFERENCES marca(id),
    proveedor_id   INTEGER REFERENCES proveedor(id),
    ubicacion_id   INTEGER REFERENCES ubicacion(id),
    precio_compra  INTEGER CHECK (precio_compra IS NULL OR precio_compra >= 0),
    precio_venta   INTEGER CHECK (precio_venta  IS NULL OR precio_venta  >= 0),
    stock_minimo   INTEGER CHECK (stock_minimo  IS NULL OR stock_minimo  >= 0),
    stock_maximo   INTEGER CHECK (stock_maximo  IS NULL OR stock_maximo  >= 0),
    observaciones  TEXT,
    activo         INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    creado_en      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    creado_por     INTEGER REFERENCES usuario(id),
    actualizado_en TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    actualizado_por INTEGER REFERENCES usuario(id),
    row_version    INTEGER NOT NULL DEFAULT 1,
    CHECK (stock_maximo IS NULL OR stock_minimo IS NULL OR stock_maximo >= stock_minimo)
);
CREATE TABLE proveedor (
    id          INTEGER PRIMARY KEY,
    nombre      TEXT NOT NULL COLLATE NOCASE UNIQUE,
    documento   TEXT,
    contacto    TEXT,
    telefono    TEXT,
    email       TEXT,
    direccion   TEXT,
    activo      INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    row_version INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE rol (
    id          INTEGER PRIMARY KEY,
    codigo      TEXT NOT NULL UNIQUE,
    nombre      TEXT NOT NULL,
    descripcion TEXT,
    es_sistema  INTEGER NOT NULL DEFAULT 0 CHECK (es_sistema IN (0,1))
);
INSERT INTO "rol" VALUES(1,'ADMIN','Administrador','Acceso total',1);
INSERT INTO "rol" VALUES(2,'OPERADOR','Operador de almacén','Productos, entradas, salidas e importaciones',1);
INSERT INTO "rol" VALUES(3,'CONSULTA','Usuario de consulta','Solo lectura, reportes y exportación',1);
CREATE TABLE rol_permiso (
    rol_id     INTEGER NOT NULL REFERENCES rol(id) ON DELETE CASCADE,
    permiso_id INTEGER NOT NULL REFERENCES permiso(id) ON DELETE CASCADE,
    PRIMARY KEY (rol_id, permiso_id)
);
INSERT INTO "rol_permiso" VALUES(1,17);
INSERT INTO "rol_permiso" VALUES(1,19);
INSERT INTO "rol_permiso" VALUES(1,3);
INSERT INTO "rol_permiso" VALUES(1,2);
INSERT INTO "rol_permiso" VALUES(1,18);
INSERT INTO "rol_permiso" VALUES(1,16);
INSERT INTO "rol_permiso" VALUES(1,13);
INSERT INTO "rol_permiso" VALUES(1,14);
INSERT INTO "rol_permiso" VALUES(1,9);
INSERT INTO "rol_permiso" VALUES(1,12);
INSERT INTO "rol_permiso" VALUES(1,10);
INSERT INTO "rol_permiso" VALUES(1,11);
INSERT INTO "rol_permiso" VALUES(1,6);
INSERT INTO "rol_permiso" VALUES(1,8);
INSERT INTO "rol_permiso" VALUES(1,7);
INSERT INTO "rol_permiso" VALUES(1,4);
INSERT INTO "rol_permiso" VALUES(1,5);
INSERT INTO "rol_permiso" VALUES(1,15);
INSERT INTO "rol_permiso" VALUES(1,1);
INSERT INTO "rol_permiso" VALUES(2,2);
INSERT INTO "rol_permiso" VALUES(2,16);
INSERT INTO "rol_permiso" VALUES(2,13);
INSERT INTO "rol_permiso" VALUES(2,14);
INSERT INTO "rol_permiso" VALUES(2,9);
INSERT INTO "rol_permiso" VALUES(2,10);
INSERT INTO "rol_permiso" VALUES(2,11);
INSERT INTO "rol_permiso" VALUES(2,6);
INSERT INTO "rol_permiso" VALUES(2,7);
INSERT INTO "rol_permiso" VALUES(2,4);
INSERT INTO "rol_permiso" VALUES(2,5);
INSERT INTO "rol_permiso" VALUES(2,15);
INSERT INTO "rol_permiso" VALUES(3,2);
INSERT INTO "rol_permiso" VALUES(3,16);
INSERT INTO "rol_permiso" VALUES(3,9);
INSERT INTO "rol_permiso" VALUES(3,4);
INSERT INTO "rol_permiso" VALUES(3,15);
CREATE TABLE tipo_movimiento (
    id             INTEGER PRIMARY KEY,
    codigo         TEXT NOT NULL UNIQUE,
    nombre         TEXT NOT NULL,
    naturaleza     TEXT NOT NULL CHECK (naturaleza IN ('ENTRADA','SALIDA','AJUSTE_POS','AJUSTE_NEG')),
    requiere_motivo INTEGER NOT NULL DEFAULT 0 CHECK (requiere_motivo IN (0,1)),
    es_sistema     INTEGER NOT NULL DEFAULT 0 CHECK (es_sistema IN (0,1)),
    activo         INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1))
);
INSERT INTO "tipo_movimiento" VALUES(1,'ENT_INICIAL','Ingreso inicial','ENTRADA',0,1,1);
INSERT INTO "tipo_movimiento" VALUES(2,'ENT_COMPRA','Compra','ENTRADA',0,0,1);
INSERT INTO "tipo_movimiento" VALUES(3,'ENT_DEVOLUCION','Devolución','ENTRADA',0,0,1);
INSERT INTO "tipo_movimiento" VALUES(4,'SAL_VENTA','Venta','SALIDA',0,0,1);
INSERT INTO "tipo_movimiento" VALUES(5,'SAL_CONSUMO','Consumo','SALIDA',0,0,1);
INSERT INTO "tipo_movimiento" VALUES(6,'SAL_ENTREGA','Entrega','SALIDA',0,0,1);
INSERT INTO "tipo_movimiento" VALUES(7,'SAL_PERDIDA','Pérdida','SALIDA',1,0,1);
INSERT INTO "tipo_movimiento" VALUES(8,'AJ_POSITIVO','Ajuste positivo','AJUSTE_POS',1,1,1);
INSERT INTO "tipo_movimiento" VALUES(9,'AJ_NEGATIVO','Ajuste negativo','AJUSTE_NEG',1,1,1);
CREATE TABLE ubicacion (
    id          INTEGER PRIMARY KEY,
    codigo      TEXT NOT NULL COLLATE NOCASE UNIQUE,
    nombre      TEXT NOT NULL,
    padre_id    INTEGER REFERENCES ubicacion(id),
    activo      INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    row_version INTEGER NOT NULL DEFAULT 1,
    CHECK (padre_id IS NULL OR padre_id <> id)
);
CREATE TABLE unidad_medida (
    id                INTEGER PRIMARY KEY,
    codigo            TEXT NOT NULL COLLATE NOCASE UNIQUE,
    nombre            TEXT NOT NULL COLLATE NOCASE UNIQUE,
    permite_decimales INTEGER NOT NULL DEFAULT 0 CHECK (permite_decimales IN (0,1)),
    activo            INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    row_version       INTEGER NOT NULL DEFAULT 1
);
INSERT INTO "unidad_medida" VALUES(1,'UND','Unidad',0,1,1);
INSERT INTO "unidad_medida" VALUES(2,'CAJ','Caja',0,1,1);
INSERT INTO "unidad_medida" VALUES(3,'PAQ','Paquete',0,1,1);
INSERT INTO "unidad_medida" VALUES(4,'KG','Kilogramo',1,1,1);
INSERT INTO "unidad_medida" VALUES(5,'LT','Litro',1,1,1);
INSERT INTO "unidad_medida" VALUES(6,'MT','Metro',1,1,1);
CREATE TABLE usuario (
    id                    INTEGER PRIMARY KEY,
    username              TEXT NOT NULL COLLATE NOCASE UNIQUE,
    nombre_completo       TEXT NOT NULL,
    password_hash         TEXT NOT NULL,
    rol_id                INTEGER NOT NULL REFERENCES rol(id),
    activo                INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    debe_cambiar_password INTEGER NOT NULL DEFAULT 0 CHECK (debe_cambiar_password IN (0,1)),
    intentos_fallidos     INTEGER NOT NULL DEFAULT 0,
    bloqueado_hasta       TEXT,
    ultimo_login          TEXT,
    creado_en             TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    actualizado_en        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    row_version           INTEGER NOT NULL DEFAULT 1
);
CREATE UNIQUE INDEX ux_producto_barras ON producto(codigo_barras)
    WHERE codigo_barras IS NOT NULL AND activo = 1;
CREATE INDEX ix_producto_nombre    ON producto(nombre COLLATE NOCASE);
CREATE INDEX ix_producto_categoria ON producto(categoria_id);
CREATE INDEX ix_producto_proveedor ON producto(proveedor_id);
CREATE INDEX ix_producto_ubicacion ON producto(ubicacion_id);
CREATE INDEX ix_producto_activo    ON producto(activo);
CREATE INDEX ix_importacion_hash ON importacion(hash_sha256);
CREATE INDEX ix_detimp_importacion ON detalle_importacion(importacion_id);
CREATE INDEX ix_mov_fecha ON movimiento(fecha_movimiento);
CREATE INDEX ix_mov_tipo  ON movimiento(tipo_movimiento_id);
CREATE INDEX ix_detmov_producto ON detalle_movimiento(producto_id, movimiento_id);
CREATE INDEX ix_detmov_mov      ON detalle_movimiento(movimiento_id);
CREATE INDEX ix_aud_fecha   ON auditoria(fecha_hora);
CREATE INDEX ix_aud_entidad ON auditoria(entidad, entidad_id);
CREATE INDEX ix_aud_usuario ON auditoria(usuario_id);
CREATE TRIGGER trg_auditoria_no_update BEFORE UPDATE ON auditoria
BEGIN SELECT RAISE(ABORT, 'auditoria es solo de anexado'); END;
CREATE TRIGGER trg_auditoria_no_delete BEFORE DELETE ON auditoria
BEGIN SELECT RAISE(ABORT, 'auditoria es solo de anexado'); END;
CREATE TRIGGER trg_movimiento_no_update BEFORE UPDATE ON movimiento
BEGIN SELECT RAISE(ABORT, 'movimiento es inmutable'); END;
CREATE TRIGGER trg_movimiento_no_delete BEFORE DELETE ON movimiento
BEGIN SELECT RAISE(ABORT, 'movimiento es inmutable'); END;
CREATE TRIGGER trg_detmov_no_update BEFORE UPDATE ON detalle_movimiento
BEGIN SELECT RAISE(ABORT, 'detalle_movimiento es inmutable'); END;
CREATE TRIGGER trg_detmov_no_delete BEFORE DELETE ON detalle_movimiento
BEGIN SELECT RAISE(ABORT, 'detalle_movimiento es inmutable'); END;
CREATE TRIGGER trg_detmov_producto_activo BEFORE INSERT ON detalle_movimiento
WHEN (SELECT activo FROM producto WHERE id = NEW.producto_id) = 0
BEGIN SELECT RAISE(ABORT, 'producto inactivo'); END;
CREATE TRIGGER trg_producto_inventario AFTER INSERT ON producto
BEGIN INSERT INTO inventario(producto_id, cantidad) VALUES (NEW.id, 0); END;
COMMIT;
