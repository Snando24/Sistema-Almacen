"""Lectura de CSV con autodetección de codificación y separador (doc 06 §1)."""

from __future__ import annotations

import csv
import hashlib
import io
from pathlib import Path

from sisalmacen.domain.errors import ValidationError
from sisalmacen.domain.importing import CsvContent

_DELIMITERS = (",", ";", "\t", "|")


class CsvFileReader:
    """Implementa `CsvReaderPort`."""

    def read(
        self,
        path: Path,
        *,
        encoding: str | None,
        delimiter: str | None,
        max_rows: int,
    ) -> CsvContent:
        raw = path.read_bytes()
        if not raw.strip():
            raise ValidationError("El archivo CSV está vacío.", code="CSV_VACIO")
        text, used_encoding = _decode(raw, encoding)
        used_delimiter = delimiter or _detect_delimiter(text)

        reader = csv.reader(io.StringIO(text, newline=""), delimiter=used_delimiter)
        headers: list[str] | None = None
        rows: list[tuple[int, dict[str, str]]] = []
        for record in reader:
            if not any(cell.strip() for cell in record):
                continue
            if headers is None:
                headers = [cell.strip() for cell in record]
                continue
            if len(rows) >= max_rows:
                raise ValidationError(
                    f"El archivo supera el máximo de {max_rows} filas.",
                    code="CSV_DEMASIADAS_FILAS",
                )
            rows.append(
                (
                    reader.line_num,
                    {headers[i]: record[i] for i in range(min(len(headers), len(record)))},
                )
            )
        if headers is None or not rows:
            raise ValidationError("El archivo no contiene filas de datos.", code="CSV_VACIO")
        return CsvContent(
            headers=headers,
            rows=rows,
            encoding=used_encoding,
            delimiter=used_delimiter,
            sha256=hashlib.sha256(raw).hexdigest(),
        )


def _decode(raw: bytes, encoding: str | None) -> tuple[str, str]:
    if encoding:
        name = "utf-8-sig" if encoding.lower().replace("_", "-") in ("utf-8", "utf8") else encoding
        try:
            return raw.decode(name), encoding
        except (UnicodeDecodeError, LookupError) as error:
            raise ValidationError(
                f"No se pudo leer el archivo con la codificación {encoding}.",
                code="CSV_CODIFICACION",
            ) from error
    try:
        return raw.decode("utf-8-sig"), "utf-8"
    except UnicodeDecodeError:
        return raw.decode("cp1252", errors="replace"), "cp1252"


def _detect_delimiter(text: str) -> str:
    first_line = next((line for line in text.splitlines() if line.strip()), "")
    counts = {delimiter: first_line.count(delimiter) for delimiter in _DELIMITERS}
    best = max(counts, key=lambda key: counts[key])
    return best if counts[best] > 0 else ","
