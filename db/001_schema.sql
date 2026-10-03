-- SisAlmacen - Esquema inicial (SQLite 3.35+). Escenario A: local.
-- Contrato de datos: los modelos SQLAlchemy y la migración Alembic inicial deben reproducirlo.
-- Convenciones: fechas TEXT ISO-8601 UTC; cantidades INTEGER x1000; dinero INTEGER x10000.
-- Requiere en cada conexión: PRAGMA foreign_keys = ON; PRAGMA journal_mode = WAL;

PRAGMA foreign_keys = ON;

-- ---------- Configuración ----------
CREATE TABLE configuracion (
    clave        TEXT PRIMARY KEY,
    valor        TEXT NOT NULL,
    descripcion  TEXT,
    actualizado_en TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

-- ---------- Seguridad ----------
CREATE TABLE rol (
    id          INTEGER PRIMARY KEY,
    codigo      TEXT NOT NULL UNIQUE,
    nombre      TEXT NOT NULL,
    descripcion TEXT,
    es_sistema  INTEGER NOT NULL DEFAULT 0 CHECK (es_sistema IN (0,1))
);

CREATE TABLE permiso (
    id          INTEGER PRIMARY KEY,
    codigo      TEXT NOT NULL UNIQUE,
    descripcion TEXT NOT NULL
);

CREATE TABLE rol_permiso (
    rol_id     INTEGER NOT NULL REFERENCES rol(id) ON DELETE CASCADE,
    permiso_id INTEGER NOT NULL REFERENCES permiso(id) ON DELETE CASCADE,
    PRIMARY KEY (rol_id, permiso_id)
);

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

-- ---------- Catálogos ----------
CREATE TABLE categoria (
    id          INTEGER PRIMARY KEY,
    nombre      TEXT NOT NULL COLLATE NOCASE UNIQUE,
    descripcion TEXT,
    activo      INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    row_version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE marca (
    id          INTEGER PRIMARY KEY,
    nombre      TEXT NOT NULL COLLATE NOCASE UNIQUE,
    activo      INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    row_version INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE unidad_medida (
    id                INTEGER PRIMARY KEY,
    codigo            TEXT NOT NULL COLLATE NOCASE UNIQUE,
    nombre            TEXT NOT NULL COLLATE NOCASE UNIQUE,
    permite_decimales INTEGER NOT NULL DEFAULT 0 CHECK (permite_decimales IN (0,1)),
    activo            INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    row_version       INTEGER NOT NULL DEFAULT 1
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

CREATE TABLE ubicacion (
    id          INTEGER PRIMARY KEY,
    codigo      TEXT NOT NULL COLLATE NOCASE UNIQUE,
    nombre      TEXT NOT NULL,
    padre_id    INTEGER REFERENCES ubicacion(id),
    activo      INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    row_version INTEGER NOT NULL DEFAULT 1,
    CHECK (padre_id IS NULL OR padre_id <> id)
);

-- ---------- Productos e inventario ----------
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
    observaciones  TEXT,
    activo         INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1)),
    creado_en      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    creado_por     INTEGER REFERENCES usuario(id),
    actualizado_en TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    actualizado_por INTEGER REFERENCES usuario(id),
    row_version    INTEGER NOT NULL DEFAULT 1
);

-- Código de barras único solo entre productos activos (RF-012).
CREATE UNIQUE INDEX ux_producto_barras ON producto(codigo_barras)
    WHERE codigo_barras IS NOT NULL AND activo = 1;
CREATE INDEX ix_producto_nombre    ON producto(nombre COLLATE NOCASE);
CREATE INDEX ix_producto_categoria ON producto(categoria_id);
CREATE INDEX ix_producto_proveedor ON producto(proveedor_id);
CREATE INDEX ix_producto_ubicacion ON producto(ubicacion_id);
CREATE INDEX ix_producto_activo    ON producto(activo);

-- Stock actual: SOLO se modifica desde MovimientoService (RF-031).
CREATE TABLE inventario (
    producto_id    INTEGER PRIMARY KEY REFERENCES producto(id),
    cantidad       INTEGER NOT NULL DEFAULT 0,
    actualizado_en TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    row_version    INTEGER NOT NULL DEFAULT 1
);

-- ---------- Movimientos ----------
CREATE TABLE tipo_movimiento (
    id             INTEGER PRIMARY KEY,
    codigo         TEXT NOT NULL UNIQUE,
    nombre         TEXT NOT NULL,
    naturaleza     TEXT NOT NULL CHECK (naturaleza IN ('ENTRADA','SALIDA','AJUSTE_POS','AJUSTE_NEG')),
    requiere_motivo INTEGER NOT NULL DEFAULT 0 CHECK (requiere_motivo IN (0,1)),
    es_sistema     INTEGER NOT NULL DEFAULT 0 CHECK (es_sistema IN (0,1)),
    activo         INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0,1))
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
CREATE INDEX ix_importacion_hash ON importacion(hash_sha256);

CREATE TABLE detalle_importacion (
    id             INTEGER PRIMARY KEY,
    importacion_id INTEGER NOT NULL REFERENCES importacion(id) ON DELETE CASCADE,
    nro_fila       INTEGER NOT NULL,
    codigo         TEXT,
    accion         TEXT NOT NULL CHECK (accion IN ('INSERTAR','ACTUALIZAR','SIN_CAMBIOS','ERROR')),
    datos_json     TEXT,
    errores_json   TEXT
);
CREATE INDEX ix_detimp_importacion ON detalle_importacion(importacion_id);

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
CREATE INDEX ix_mov_fecha ON movimiento(fecha_movimiento);
CREATE INDEX ix_mov_tipo  ON movimiento(tipo_movimiento_id);

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
CREATE INDEX ix_detmov_producto ON detalle_movimiento(producto_id, movimiento_id);
CREATE INDEX ix_detmov_mov      ON detalle_movimiento(movimiento_id);

-- ---------- Auditoría ----------
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
CREATE INDEX ix_aud_fecha   ON auditoria(fecha_hora);
CREATE INDEX ix_aud_entidad ON auditoria(entidad, entidad_id);
CREATE INDEX ix_aud_usuario ON auditoria(usuario_id);

-- ---------- Integridad por triggers ----------
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

-- RN-007: no mover productos inactivos.
CREATE TRIGGER trg_detmov_producto_activo BEFORE INSERT ON detalle_movimiento
WHEN (SELECT activo FROM producto WHERE id = NEW.producto_id) = 0
BEGIN SELECT RAISE(ABORT, 'producto inactivo'); END;

-- Todo producto nuevo nace con su fila de inventario en cero.
CREATE TRIGGER trg_producto_inventario AFTER INSERT ON producto
BEGIN INSERT INTO inventario(producto_id, cantidad) VALUES (NEW.id, 0); END;
