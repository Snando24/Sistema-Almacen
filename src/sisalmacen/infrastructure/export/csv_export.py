"""Exportación a CSV (RF-090) e informe de errores de importación."""

from __future__ import annotations

import csv
from collections.abc import Mapping, Sequence
from pathlib import Path

from sisalmacen.domain.inventory import ReportData
from sisalmacen.infrastructure.export.formatting import cell_text


class CsvReportWriter:
    """Implementa `ReportWriterPort` para CSV (UTF-8 con BOM, abre bien en Excel)."""

    def write(self, path: Path, data: ReportData, *, company: Mapping[str, str]) -> None:
        del company
        rows = [
            [cell_text(value, kind) for value, kind in zip(row, data.column_types, strict=False)]
            for row in data.rows
        ]
        if data.totals is not None:
            rows.append(
                [
                    cell_text(value, kind)
                    for value, kind in zip(data.totals, data.column_types, strict=False)
                ]
            )
        write_rows(path, [data.headers, *rows])


def write_rows(path: Path, rows: Sequence[Sequence[str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        csv.writer(handle).writerows(rows)
