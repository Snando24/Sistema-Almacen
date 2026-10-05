"""Alinea la configuración inicial con el modelo operativo de R&R."""

from __future__ import annotations

from typing import Final

from alembic import op

revision: Final[str] = "0003_rr_product_model"
down_revision: Final[str] = "0002_theme_preference"
branch_labels: Final[tuple[str, ...] | None] = None
depends_on: Final[tuple[str, ...] | None] = None

_CATEGORIES = (
    "SOLDADURA CORTE Y GASES",
    "ABRASIVOS CORTE Y DESBASTE",
    "ACEROS Y MATERIALES",
    "FERRETERIA Y FIJACIONES",
    "REPARACION DE NEUMATICOS",
    "ELECTRICIDAD E ILUMINACION",
    "PINTURAS ADHESIVOS Y QUIMICOS",
    "FRENOS Y SUSPENSION",
    "REPUESTOS DE MAQUINARIA PESADA",
    "NEUMATICA Y LUBRICACION",
    "MAQUINARIA Y EQUIPOS DE TALLER",
    "HERRAMIENTAS ELECTRICAS Y NEUMATICAS",
    "HERRAMIENTAS MANUALES",
    "IZAJE Y ELEVACION",
    "EPP Y SEGURIDAD",
    "OFICINA Y PAPELERIA",
    "INFORMATICA E IMPRESION",
)


def upgrade() -> None:
    for category in _CATEGORIES:
        escaped = category.replace("'", "''")
        op.execute(f"INSERT OR IGNORE INTO categoria (nombre) VALUES ('{escaped}')")
    op.execute("UPDATE configuracion SET valor = '0' WHERE clave = 'inventario.usar_stock_maximo'")


def downgrade() -> None:
    # Las categorías son catálogos editables y pueden estar referenciadas por productos.
    # Por seguridad, una reversión no borra datos operativos.
    op.execute("UPDATE configuracion SET valor = '1' WHERE clave = 'inventario.usar_stock_maximo'")
