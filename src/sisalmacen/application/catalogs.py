"""Casos de uso de catálogos (HU-02.1)."""

from __future__ import annotations

from typing import Any

from sisalmacen.application.auditing import AuditRecorder
from sisalmacen.application.auth import AuthorizationService, CurrentSession
from sisalmacen.application.ports import WorkUnitFactory
from sisalmacen.domain.errors import (
    BusinessRuleViolation,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from sisalmacen.domain.inventory import CATALOG_KINDS, CatalogKind


class CatalogService:
    """CRUD con baja lógica de categorías, marcas, unidades, proveedores y ubicaciones."""

    def __init__(
        self,
        uow_factory: WorkUnitFactory,
        actor: CurrentSession,
        authorization: AuthorizationService | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._actor = actor
        self._authz = authorization or AuthorizationService()
        self._audit = AuditRecorder(actor)

    def list_entries(self, kind: str, *, include_inactive: bool = True) -> list[dict[str, Any]]:
        self._authz.require_permission(self._actor, "catalogos.ver")
        _kind_spec(kind)
        with self._uow_factory() as uow:
            return uow.catalogs.list_entries(kind, include_inactive=include_inactive)

    def create(self, kind: str, data: dict[str, Any]) -> int:
        self._authz.require_permission(self._actor, "catalogos.gestionar")
        spec = _kind_spec(kind)
        clean = _clean(spec, data)
        with self._uow_factory() as uow:
            self._ensure_unique(uow, spec, clean, exclude_id=None)
            self._ensure_parent(uow, spec, clean, entry_id=None)
            entry_id = uow.catalogs.add(kind, clean)
            self._audit.record(uow, "CREAR", kind, entry_id, new=clean)
            uow.commit()
        return entry_id

    def update(self, kind: str, entry_id: int, data: dict[str, Any]) -> None:
        self._authz.require_permission(self._actor, "catalogos.gestionar")
        spec = _kind_spec(kind)
        clean = _clean(spec, data)
        with self._uow_factory() as uow:
            current = uow.catalogs.get(kind, entry_id)
            if current is None:
                raise NotFoundError("No se encontró el registro.", code="CATALOGO_NO_ENCONTRADO")
            self._ensure_unique(uow, spec, clean, exclude_id=entry_id)
            self._ensure_parent(uow, spec, clean, entry_id=entry_id)
            uow.catalogs.update(kind, entry_id, clean)
            previous = {key: current.get(key) for key in clean}
            self._audit.record(uow, "EDITAR", kind, entry_id, previous=previous, new=clean)
            uow.commit()

    def set_active(self, kind: str, entry_id: int, *, active: bool) -> None:
        self._authz.require_permission(self._actor, "catalogos.gestionar")
        _kind_spec(kind)
        with self._uow_factory() as uow:
            current = uow.catalogs.get(kind, entry_id)
            if current is None:
                raise NotFoundError("No se encontró el registro.", code="CATALOGO_NO_ENCONTRADO")
            if not active:
                in_use = uow.catalogs.count_active_products_using(kind, entry_id)
                if in_use:
                    raise BusinessRuleViolation(
                        f"No se puede desactivar: lo usan {in_use} producto(s) activo(s).",
                        code="CATALOGO_EN_USO",
                    )
            uow.catalogs.set_active(kind, entry_id, active=active)
            self._audit.record(
                uow,
                "ACTIVAR" if active else "DESACTIVAR",
                kind,
                entry_id,
                previous={"activo": bool(current.get("activo"))},
                new={"activo": active},
            )
            uow.commit()

    @staticmethod
    def _ensure_unique(
        uow: Any, spec: CatalogKind, clean: dict[str, Any], *, exclude_id: int | None
    ) -> None:
        for field_name in spec.unique_fields:
            value = clean.get(field_name)
            if value is None:
                continue
            if uow.catalogs.find(spec.key, field_name, str(value), exclude_id=exclude_id):
                raise ConflictError(
                    f"Ya existe {spec.singular.lower()} con {field_name} '{value}'.",
                    code="CATALOGO_DUPLICADO",
                )

    @staticmethod
    def _ensure_parent(
        uow: Any, spec: CatalogKind, clean: dict[str, Any], *, entry_id: int | None
    ) -> None:
        parent_id = clean.get("padre_id")
        if spec.key != "ubicacion" or parent_id is None:
            return
        if entry_id is not None and parent_id == entry_id:
            raise ValidationError(
                "Una ubicación no puede ser su propio padre.", code="UBICACION_CICLO"
            )
        visited: set[int] = set()
        cursor: int | None = parent_id
        while cursor is not None:
            if cursor in visited or (entry_id is not None and cursor == entry_id):
                raise ValidationError(
                    "La jerarquía de ubicaciones no puede ser circular.", code="UBICACION_CICLO"
                )
            visited.add(cursor)
            parent = uow.catalogs.get("ubicacion", cursor)
            if parent is None:
                raise NotFoundError("La ubicación padre no existe.", code="UBICACION_PADRE")
            cursor = parent.get("padre_id")


def _kind_spec(kind: str) -> CatalogKind:
    spec = CATALOG_KINDS.get(kind)
    if spec is None:
        raise ValidationError(f"Catálogo desconocido: {kind}.", code="CATALOGO_DESCONOCIDO")
    return spec


def _clean(spec: CatalogKind, data: dict[str, Any]) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    for field_spec in spec.fields:
        raw = data.get(field_spec.name)
        if field_spec.kind == "bool":
            clean[field_spec.name] = bool(raw)
            continue
        if field_spec.kind == "ref":
            clean[field_spec.name] = int(raw) if raw not in (None, "") else None
            continue
        text = "" if raw is None else str(raw).strip()
        if not text:
            if field_spec.required:
                raise ValidationError(
                    f"Debe indicar {field_spec.label.lower()}.",
                    code="CATALOGO_CAMPO_REQUERIDO",
                )
            clean[field_spec.name] = None
            continue
        if len(text) > field_spec.max_len:
            raise ValidationError(
                f"{field_spec.label} excede {field_spec.max_len} caracteres.",
                code="CATALOGO_LONGITUD",
            )
        clean[field_spec.name] = text
    return clean
