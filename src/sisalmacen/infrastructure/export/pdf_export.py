"""Exportación a PDF con reportlab (RF-092/095)."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from sisalmacen.domain.inventory import ReportData
from sisalmacen.infrastructure.export.formatting import cell_text

_RED = colors.HexColor("#d1121e")
_DARK = colors.HexColor("#101214")
_RIGHT_ALIGNED = {"qty", "money", "int"}


class PdfReportWriter:
    """Implementa `ReportWriterPort` para PDF con logo, empresa, fecha, filtros y paginación."""

    def write(self, path: Path, data: ReportData, *, company: Mapping[str, str]) -> None:
        page = landscape(A4) if len(data.headers) > 6 else A4
        document = SimpleDocTemplate(
            str(path),
            pagesize=page,
            leftMargin=12 * mm,
            rightMargin=12 * mm,
            topMargin=12 * mm,
            bottomMargin=14 * mm,
            title=data.title,
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("T", parent=styles["Title"], textColor=_DARK, fontSize=16)
        meta_style = ParagraphStyle("M", parent=styles["Normal"], fontSize=8, leading=10)
        cell_style = ParagraphStyle("C", parent=styles["Normal"], fontSize=7.5, leading=9)
        right_style = ParagraphStyle("R", parent=cell_style, alignment=2)
        head_style = ParagraphStyle(
            "H", parent=cell_style, textColor=colors.white, fontName="Helvetica-Bold"
        )

        story: list[Any] = []
        logo = _logo(company.get("empresa.logo_ruta", ""))
        if logo is not None:
            story.append(logo)
        name = company.get("empresa.nombre", "")
        if name:
            story.append(Paragraph(f"<b>{escape(name)}</b>", styles["Heading3"]))
        extra = " · ".join(
            part
            for part in (
                company.get("empresa.documento", ""),
                company.get("empresa.direccion", ""),
                company.get("empresa.telefono", ""),
            )
            if part
        )
        if extra:
            story.append(Paragraph(escape(extra), meta_style))
        story.append(Paragraph(escape(data.title), title_style))
        story.append(
            Paragraph(f"Generado: {datetime.now().astimezone():%Y-%m-%d %H:%M}", meta_style)
        )
        if data.filters:
            story.append(Paragraph("Filtros: " + escape(" | ".join(data.filters)), meta_style))
        story.append(Spacer(1, 4 * mm))

        table_rows: list[list[Any]] = [[Paragraph(escape(h), head_style) for h in data.headers]]
        for row in [*data.rows, *([data.totals] if data.totals is not None else [])]:
            table_rows.append(
                [
                    Paragraph(
                        escape(cell_text(value, kind)),
                        right_style if kind in _RIGHT_ALIGNED else cell_style,
                    )
                    for value, kind in zip(row, data.column_types, strict=False)
                ]
            )
        if len(table_rows) == 1:
            story.append(Paragraph("Sin datos para los criterios seleccionados.", meta_style))
        else:
            available = page[0] - 24 * mm
            table = Table(
                table_rows, colWidths=_column_widths(data, available), repeatRows=1
            )
            style = [
                ("BACKGROUND", (0, 0), (-1, 0), _RED),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f6f4")]),
            ]
            if data.totals is not None:
                style.append(("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f2b93b")))
            table.setStyle(TableStyle(style))
            story.append(table)

        document.build(story, onFirstPage=_footer, onLaterPages=_footer)


def _column_widths(data: ReportData, available: float) -> list[float]:
    lengths: list[int] = []
    for index, header in enumerate(data.headers):
        longest = len(header)
        for row in data.rows[:200]:
            if index < len(row):
                longest = max(longest, len(cell_text(row[index], data.column_types[index])))
        lengths.append(min(max(longest, 4), 40))
    total = sum(lengths)
    return [available * length / total for length in lengths]


def _logo(path_text: str) -> Image | None:
    if not path_text:
        return None
    path = Path(path_text)
    if not path.is_file():
        return None
    try:
        width, height = ImageReader(str(path)).getSize()
    except Exception:
        return None
    target_height = 14 * mm
    return Image(str(path), width=target_height * width / height, height=target_height, hAlign="LEFT")


def _footer(canvas: Any, document: Any) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(document.pagesize[0] - 12 * mm, 8 * mm, f"Página {document.page}")
    canvas.restoreState()
