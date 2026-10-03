"""Modelos SQLAlchemy base de SisAlmacen."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from sisalmacen.infrastructure.db.base import Base
from sisalmacen.infrastructure.db.types import ScaledMoney, ScaledQuantity

UTC_NOW_SQL = text("(strftime('%Y-%m-%dT%H:%M:%SZ','now'))")


class Configuracion(Base):
    __tablename__ = "configuracion"

    clave: Mapped[str] = mapped_column(String, primary_key=True)
    valor: Mapped[str] = mapped_column(String, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    actualizado_en: Mapped[str] = mapped_column(String, nullable=False, server_default=UTC_NOW_SQL)


class Rol(Base):
    __tablename__ = "rol"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    es_sistema: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))


class Permiso(Base):
    __tablename__ = "permiso"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)


class RolPermiso(Base):
    __tablename__ = "rol_permiso"

    rol_id: Mapped[int] = mapped_column(ForeignKey("rol.id", ondelete="CASCADE"), primary_key=True)
    permiso_id: Mapped[int] = mapped_column(
        ForeignKey("permiso.id", ondelete="CASCADE"),
        primary_key=True,
    )


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(collation="NOCASE"), nullable=False, unique=True)
    nombre_completo: Mapped[str] = mapped_column(String, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    rol_id: Mapped[int] = mapped_column(ForeignKey("rol.id"), nullable=False)
    activo: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    debe_cambiar_password: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    intentos_fallidos: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    bloqueado_hasta: Mapped[str | None] = mapped_column(String)
    ultimo_login: Mapped[str | None] = mapped_column(String)
    creado_en: Mapped[str] = mapped_column(String, nullable=False, server_default=UTC_NOW_SQL)
    actualizado_en: Mapped[str] = mapped_column(String, nullable=False, server_default=UTC_NOW_SQL)
    row_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class Categoria(Base):
    __tablename__ = "categoria"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(collation="NOCASE"), nullable=False, unique=True)
    descripcion: Mapped[str | None] = mapped_column(Text)
    activo: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    row_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class Marca(Base):
    __tablename__ = "marca"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(collation="NOCASE"), nullable=False, unique=True)
    activo: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    row_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class UnidadMedida(Base):
    __tablename__ = "unidad_medida"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(collation="NOCASE"), nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(String(collation="NOCASE"), nullable=False, unique=True)
    permite_decimales: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    activo: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    row_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class Proveedor(Base):
    __tablename__ = "proveedor"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(collation="NOCASE"), nullable=False, unique=True)
    documento: Mapped[str | None] = mapped_column(String)
    contacto: Mapped[str | None] = mapped_column(String)
    telefono: Mapped[str | None] = mapped_column(String)
    email: Mapped[str | None] = mapped_column(String)
    direccion: Mapped[str | None] = mapped_column(Text)
    activo: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    row_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class Ubicacion(Base):
    __tablename__ = "ubicacion"
    __table_args__ = (
        CheckConstraint("padre_id IS NULL OR padre_id <> id", name="ubicacion_padre_distinto"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(collation="NOCASE"), nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    padre_id: Mapped[int | None] = mapped_column(ForeignKey("ubicacion.id"))
    activo: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    row_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class Producto(Base):
    __tablename__ = "producto"
    __table_args__ = (
        CheckConstraint(
            "stock_maximo IS NULL OR stock_minimo IS NULL OR stock_maximo >= stock_minimo",
            name="producto_stock_max_ge_min",
        ),
        Index(
            "ux_producto_barras",
            "codigo_barras",
            unique=True,
            sqlite_where=text("codigo_barras IS NOT NULL AND activo = 1"),
        ),
        Index("ix_producto_nombre", "nombre"),
        Index("ix_producto_categoria", "categoria_id"),
        Index("ix_producto_proveedor", "proveedor_id"),
        Index("ix_producto_ubicacion", "ubicacion_id"),
        Index("ix_producto_activo", "activo"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(collation="NOCASE"), nullable=False, unique=True)
    codigo_barras: Mapped[str | None] = mapped_column(String)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categoria.id"), nullable=False)
    unidad_id: Mapped[int] = mapped_column(ForeignKey("unidad_medida.id"), nullable=False)
    marca_id: Mapped[int | None] = mapped_column(ForeignKey("marca.id"))
    proveedor_id: Mapped[int | None] = mapped_column(ForeignKey("proveedor.id"))
    ubicacion_id: Mapped[int | None] = mapped_column(ForeignKey("ubicacion.id"))
    precio_compra: Mapped[Decimal | None] = mapped_column(ScaledMoney())
    precio_venta: Mapped[Decimal | None] = mapped_column(ScaledMoney())
    stock_minimo: Mapped[Decimal | None] = mapped_column(ScaledQuantity())
    stock_maximo: Mapped[Decimal | None] = mapped_column(ScaledQuantity())
    observaciones: Mapped[str | None] = mapped_column(Text)
    activo: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    creado_en: Mapped[str] = mapped_column(String, nullable=False, server_default=UTC_NOW_SQL)
    creado_por: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"))
    actualizado_en: Mapped[str] = mapped_column(String, nullable=False, server_default=UTC_NOW_SQL)
    actualizado_por: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"))
    row_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class Inventario(Base):
    __tablename__ = "inventario"

    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id"), primary_key=True)
    cantidad: Mapped[Decimal] = mapped_column(
        ScaledQuantity(), nullable=False, server_default=text("0")
    )
    actualizado_en: Mapped[str] = mapped_column(String, nullable=False, server_default=UTC_NOW_SQL)
    row_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class TipoMovimiento(Base):
    __tablename__ = "tipo_movimiento"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    naturaleza: Mapped[str] = mapped_column(String, nullable=False)
    requiere_motivo: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    es_sistema: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    activo: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class Importacion(Base):
    __tablename__ = "importacion"
    __table_args__ = (Index("ix_importacion_hash", "hash_sha256"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_archivo: Mapped[str] = mapped_column(String, nullable=False)
    hash_sha256: Mapped[str] = mapped_column(String, nullable=False)
    modo: Mapped[str] = mapped_column(String, nullable=False)
    aplicar_stock: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    iniciado_en: Mapped[str] = mapped_column(String, nullable=False, server_default=UTC_NOW_SQL)
    finalizado_en: Mapped[str | None] = mapped_column(String)
    estado: Mapped[str] = mapped_column(String, nullable=False)
    total_filas: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    filas_nuevas: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    filas_actualizables: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    filas_error: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    insertados: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    actualizados: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    rechazados: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))


class DetalleImportacion(Base):
    __tablename__ = "detalle_importacion"
    __table_args__ = (Index("ix_detimp_importacion", "importacion_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    importacion_id: Mapped[int] = mapped_column(
        ForeignKey("importacion.id", ondelete="CASCADE"),
        nullable=False,
    )
    nro_fila: Mapped[int] = mapped_column(Integer, nullable=False)
    codigo: Mapped[str | None] = mapped_column(String)
    accion: Mapped[str] = mapped_column(String, nullable=False)
    datos_json: Mapped[str | None] = mapped_column(Text)
    errores_json: Mapped[str | None] = mapped_column(Text)


class Movimiento(Base):
    __tablename__ = "movimiento"
    __table_args__ = (
        Index("ix_mov_fecha", "fecha_movimiento"),
        Index("ix_mov_tipo", "tipo_movimiento_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tipo_movimiento_id: Mapped[int] = mapped_column(
        ForeignKey("tipo_movimiento.id"), nullable=False
    )
    fecha_movimiento: Mapped[str] = mapped_column(String, nullable=False)
    creado_en: Mapped[str] = mapped_column(String, nullable=False, server_default=UTC_NOW_SQL)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    motivo: Mapped[str | None] = mapped_column(Text)
    documento_referencia: Mapped[str | None] = mapped_column(String)
    observacion: Mapped[str | None] = mapped_column(Text)
    importacion_id: Mapped[int | None] = mapped_column(ForeignKey("importacion.id"))
    movimiento_origen_id: Mapped[int | None] = mapped_column(ForeignKey("movimiento.id"))


class DetalleMovimiento(Base):
    __tablename__ = "detalle_movimiento"
    __table_args__ = (
        CheckConstraint("signo IN (-1,1)", name="detalle_movimiento_signo_valido"),
        CheckConstraint("cantidad > 0", name="detalle_movimiento_cantidad_positiva"),
        CheckConstraint(
            "stock_resultante = stock_anterior + signo * cantidad",
            name="detalle_movimiento_stock_consistente",
        ),
        Index("ix_detmov_producto", "producto_id", "movimiento_id"),
        Index("ix_detmov_mov", "movimiento_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    movimiento_id: Mapped[int] = mapped_column(ForeignKey("movimiento.id"), nullable=False)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id"), nullable=False)
    signo: Mapped[int] = mapped_column(Integer, nullable=False)
    cantidad: Mapped[Decimal] = mapped_column(ScaledQuantity(), nullable=False)
    stock_anterior: Mapped[Decimal] = mapped_column(ScaledQuantity(), nullable=False)
    stock_resultante: Mapped[Decimal] = mapped_column(ScaledQuantity(), nullable=False)
    precio_unitario: Mapped[Decimal | None] = mapped_column(ScaledMoney())


class Auditoria(Base):
    __tablename__ = "auditoria"
    __table_args__ = (
        Index("ix_aud_fecha", "fecha_hora"),
        Index("ix_aud_entidad", "entidad", "entidad_id"),
        Index("ix_aud_usuario", "usuario_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fecha_hora: Mapped[str] = mapped_column(String, nullable=False, server_default=UTC_NOW_SQL)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"))
    username: Mapped[str | None] = mapped_column(String)
    accion: Mapped[str] = mapped_column(String, nullable=False)
    entidad: Mapped[str] = mapped_column(String, nullable=False)
    entidad_id: Mapped[str | None] = mapped_column(String)
    valor_anterior: Mapped[str | None] = mapped_column(Text)
    valor_nuevo: Mapped[str | None] = mapped_column(Text)
    detalle: Mapped[str | None] = mapped_column(Text)
    estacion: Mapped[str | None] = mapped_column(String)
