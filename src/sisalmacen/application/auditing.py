"""Registro de auditoría dentro de la misma transacción del caso de uso (RB-14)."""

from __future__ import annotations

import json
import socket
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sisalmacen.application.auth import CurrentSession
from sisalmacen.application.ports import WorkUnit


def to_json(value: Any) -> str | None:
    """Serializa a JSON estable; `None` se conserva como NULL."""

    if value is None:
        return None
    if is_dataclass(value) and not isinstance(value, type):
        value = asdict(value)
    return json.dumps(value, ensure_ascii=False, default=_json_default, sort_keys=True)


def _json_default(value: object) -> str:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, date | datetime):
        return value.isoformat()
    return str(value)


class AuditRecorder:
    """Agrega registros de auditoría atribuidos al usuario actual."""

    def __init__(self, actor: CurrentSession) -> None:
        self._actor = actor
        self._station = socket.gethostname()

    def record(
        self,
        uow: WorkUnit,
        action: str,
        entity: str,
        entity_id: object | None = None,
        *,
        previous: Any = None,
        new: Any = None,
        detail: str | None = None,
    ) -> None:
        uow.audit.add(
            user_id=self._actor.user_id,
            username=self._actor.username,
            action=action,
            entity=entity,
            entity_id=None if entity_id is None else str(entity_id),
            previous=to_json(previous),
            new=to_json(new),
            detail=detail,
            station=self._station,
        )
