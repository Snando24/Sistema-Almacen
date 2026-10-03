"""Añade la preferencia persistente de tema visual."""

from __future__ import annotations

from typing import Final

from alembic import op

revision: Final[str] = "0002_theme_preference"
down_revision: Final[str] = "0001_initial"
branch_labels: Final[tuple[str, ...] | None] = None
depends_on: Final[tuple[str, ...] | None] = None


def upgrade() -> None:
    op.execute(
        "INSERT OR IGNORE INTO configuracion (clave, valor, descripcion) "
        "VALUES ('ui.tema', 'claro', 'Tema visual: claro u oscuro')"
    )


def downgrade() -> None:
    op.execute("DELETE FROM configuracion WHERE clave = 'ui.tema'")
