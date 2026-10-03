"""Tipos del flujo de importación CSV (doc 06)."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

MODES = ("INSERTAR", "ACTUALIZAR", "INSERTAR_ACTUALIZAR")

ACTION_INSERT = "INSERTAR"
ACTION_UPDATE = "ACTUALIZAR"
ACTION_NO_CHANGE = "SIN_CAMBIOS"
ACTION_ERROR = "ERROR"

CLEAR_TOKEN = "[BORRAR]"  # noqa: S105

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
    "stock",
    "estado",
    "observaciones",
)
REQUIRED_FOR_INSERT = ("nombre", "categoria", "unidad")


@dataclass(frozen=True)
class CsvContent:
    headers: list[str]
    rows: list[tuple[int, dict[str, str]]]
    encoding: str
    delimiter: str
    sha256: str


@dataclass(frozen=True)
class ImportOptions:
    mode: str = "INSERTAR_ACTUALIZAR"
    encoding: str | None = None
    delimiter: str | None = None
    decimal_separator: str = "."
    create_missing_catalogs: bool = False
    apply_stock: bool = False
    skip_error_rows: bool = False


@dataclass(frozen=True)
class RowError:
    code: str
    column: str
    message: str
    original: str = ""


@dataclass(frozen=True)
class PendingCatalog:
    """Catálogo que se creará al aplicar (opción "crear catálogos faltantes")."""

    kind: str
    name: str


@dataclass
class RowResult:
    nro_fila: int
    codigo: str
    accion: str
    errors: list[RowError] = field(default_factory=list)
    values: dict[str, Any] = field(default_factory=dict)
    stock: Decimal | None = None
    existing_id: int | None = None
    raw: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ExistingProduct:
    id: int
    codigo: str
    nombre: str
    activo: bool
    unidad_id: int
    categoria_id: int
    marca_id: int | None
    proveedor_id: int | None
    ubicacion_id: int | None
    codigo_barras: str | None
    descripcion: str | None
    precio_compra: Decimal | None
    precio_venta: Decimal | None
    stock_minimo: Decimal | None
    stock_maximo: Decimal | None
    observaciones: str | None
    cantidad: Decimal
    has_movements: bool


@dataclass(frozen=True)
class UnitInfo:
    id: int
    permite_decimales: bool


@dataclass
class ImportLookups:
    categorias: dict[str, int]
    marcas: dict[str, int]
    proveedores: dict[str, int]
    ubicaciones: dict[str, int]
    unidades: dict[str, UnitInfo]
    unidades_por_id: dict[int, UnitInfo]
    productos: dict[str, ExistingProduct]
    barcodes: dict[str, str]  # código de barras ? código de producto activo


@dataclass(frozen=True)
class ImportRecord:
    id: int
    nombre_archivo: str
    hash_sha256: str
    modo: str
    aplicar_stock: bool
    usuario_id: int
    iniciado_en: str
    finalizado_en: str | None
    estado: str
    total_filas: int
    filas_nuevas: int
    filas_actualizables: int
    filas_error: int
    insertados: int
    actualizados: int
    rechazados: int


@dataclass(frozen=True)
class ImportDetail:
    nro_fila: int
    codigo: str | None
    accion: str
    datos: dict[str, str]
    errores: list[dict[str, str]]


@dataclass
class ImportPreview:
    importacion_id: int
    archivo: str
    sha256: str
    total: int
    nuevas: int
    actualizables: int
    sin_cambios: int
    errores: int
    rows: list[RowResult]
    warnings: list[str] = field(default_factory=list)
    repetido: ImportRecord | None = None


@dataclass(frozen=True)
class ImportResult:
    importacion_id: int
    insertados: int
    actualizados: int
    sin_cambios: int
    rechazados: int
    movimientos: int
