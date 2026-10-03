"""Exportación de datos a CSV para productos y movimientos."""

from __future__ import annotations

from io import StringIO

from csv import DictWriter

from datetime import date

from decimal import Decimal

from typing import Any, Sequence


def export_to_csv(
    headers: Sequence[str], rows: Sequence[dict[str, Any]], *, has_bom: bool = True
) -> str:
    """Exporta datos a formato CSV con UTF-8 BOM para compatibilidad Excel."""

    output = StringIO()

    # UTF-8 BOM para compatibilidad con Excel
    if has_bom:
        output.write("\ufeff")

    writer = DictWriter(output, fieldnames=headers)
    writer.writeheader()

    for row in rows:
        # Convertir valores especiales
        cleaned_row = {}
        for key, value in row.items():
            if key not in headers:
                continue
            if value is None:
                cleaned_row[key] = ""
            elif isinstance(value, bool):
                cleaned_row[key] = "ACTIVO" if value else "INACTIVO"
            elif isinstance(value, Decimal):
                cleaned_row[key] = str(value)
            elif isinstance(value, date):
                cleaned_row[key] = value.isoformat()
            else:
                cleaned_row[key] = str(value)
        writer.writerow(cleaned_row)

    return output.getvalue()


# Formatos oficiales de productos
PRODUCTOS_CSV_HEADERS = [
    "codigo_producto",
    "descripcion",
    "descripcion_adicional",
    "marca",
    "categoria",
    "precio_compra",
    "precio_venta",
    "stock_minimo",
    "stock_inicial",
    "entradas",
    "salidas",
    "stock_actual",
    "almacen",
    "ubicacion",
    "proveedor",
    "fecha_registro",
    "estado",
    "observacion",
]

# Formatos oficiales de movimientos
MOVIMIENTOS_CSV_HEADERS = [
    "tipo_movimiento",
    "fecha",
    "codigo_producto",
    "descripcion",
    "cantidad",
    "um",
    "documento",
    "almacen",
    "ubicacion",
    "proveedor",
    "observacion",
]
