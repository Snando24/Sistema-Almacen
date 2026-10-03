"""Repositorios SQLAlchemy de movimientos y auditoría."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from sisalmacen.domain.inventory import (
    ZERO,
    AuditFilter,
    AuditRow,
    MovementFilter,
    MovementRow,
    MovementType,
    Page,
)
from sisalmacen.infrastructure.db.catalog_product_repositories import utc_now
from sisalmacen.infrastructure.db.models import (
    Auditoria,
    DetalleMovimiento,
    Inventario,
    Movimiento,
    Producto,
    TipoMovimiento,
    Usuario,
)


def _to_type(model: TipoMovimiento) -> MovementType:
    return MovementType(
        id=model.id,
        codigo=model.codigo,
        nombre=model.nombre,
        naturaleza=model.naturaleza,
        requiere_motivo=bool(model.requiere_motivo),
        es_sistema=bool(model.es_sistema),
        activo=bool(model.activo),
    )


def _movement_conditions(movement_filter: MovementFilter) -> list[Any]:
    conditions: list[Any] = []
    if movement_filter.producto_id is not None:
        conditions.append(DetalleMovimiento.producto_id == movement_filter.producto_id)
    if movement_filter.movimiento_id is not None:
        conditions.append(Movimiento.id == movement_filter.movimiento_id)
    if movement_filter.tipo_codigo:
        conditions.append(TipoMovimiento.codigo == movement_filter.tipo_codigo)
    if movement_filter.usuario_id is not None:
        conditions.append(Movimiento.usuario_id == movement_filter.usuario_id)
    if movement_filter.fecha_desde is not None:
        conditions.append(Movimiento.fecha_movimiento >= movement_filter.fecha_desde.isoformat())
    if movement_filter.fecha_hasta is not None:
        conditions.append(Movimiento.fecha_movimiento <= movement_filter.fecha_hasta.isoformat())
    return conditions


class SqlAlchemyMovementRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    # ----- tipos -----

    def get_type(self, code: str) -> MovementType | None:
        model = self._session.execute(
            select(TipoMovimiento).where(TipoMovimiento.codigo == code)
        ).scalar_one_or_none()
        return None if model is None else _to_type(model)

    def list_types(self, *, include_inactive: bool = True) -> list[MovementType]:
        statement = select(TipoMovimiento).order_by(TipoMovimiento.naturaleza, TipoMovimiento.nombre)
        if not include_inactive:
            statement = statement.where(TipoMovimiento.activo == 1)
        return [_to_type(model) for model in self._session.execute(statement).scalars()]

    def add_type(self, code: str, name: str, nature: str, *, requires_reason: bool) -> int:
        model = TipoMovimiento(
            codigo=code,
            nombre=name,
            naturaleza=nature,
            requiere_motivo=1 if requires_reason else 0,
            es_sistema=0,
            activo=1,
        )
        self._session.add(model)
        self._session.flush()
        return int(model.id)

    def update_type(self, type_id: int, name: str, *, requires_reason: bool) -> None:
        model = self._session.get(TipoMovimiento, type_id)
        if model is None:
            raise RuntimeError("Tipo de movimiento inexistente.")
        model.nombre = name
        model.requiere_motivo = 1 if requires_reason else 0
        self._session.flush()

    def set_type_active(self, type_id: int, *, active: bool) -> None:
        model = self._session.get(TipoMovimiento, type_id)
        if model is None:
            raise RuntimeError("Tipo de movimiento inexistente.")
        model.activo = 1 if active else 0
        self._session.flush()

    # ----- stock y movimientos -----

    def get_stock(self, product_id: int) -> Decimal:
        row = self._session.get(Inventario, product_id)
        return ZERO if row is None else row.cantidad

    def set_stock(self, product_id: int, quantity: Decimal) -> None:
        row = self._session.get(Inventario, product_id)
        if row is None:
            raise RuntimeError("El producto no tiene fila de inventario.")
        row.cantidad = quantity
        row.actualizado_en = utc_now()
        row.row_version += 1
        self._session.flush()

    def add_movement(
        self,
        *,
        type_id: int,
        movement_date: date,
        user_id: int,
        reason: str | None,
        reference: str | None,
        note: str | None,
        import_id: int | None,
        origin_id: int | None,
    ) -> int:
        model = Movimiento(
            tipo_movimiento_id=type_id,
            fecha_movimiento=movement_date.isoformat(),
            creado_en=utc_now(),
            usuario_id=user_id,
            motivo=reason,
            documento_referencia=reference,
            observacion=note,
            importacion_id=import_id,
            movimiento_origen_id=origin_id,
        )
        self._session.add(model)
        self._session.flush()
        return int(model.id)

    def add_detail(
        self,
        *,
        movement_id: int,
        product_id: int,
        sign: int,
        quantity: Decimal,
        previous: Decimal,
        resulting: Decimal,
        unit_price: Decimal | None,
    ) -> None:
        self._session.add(
            DetalleMovimiento(
                movimiento_id=movement_id,
                producto_id=product_id,
                signo=sign,
                cantidad=quantity,
                stock_anterior=previous,
                stock_resultante=resulting,
                precio_unitario=unit_price,
            )
        )
        self._session.flush()

    def search(
        self, movement_filter: MovementFilter, *, page: int = 1, page_size: int = 100
    ) -> Page[MovementRow]:
        conditions = _movement_conditions(movement_filter)
        total = self._session.execute(
            select(func.count(DetalleMovimiento.id))
            .select_from(Movimiento)
            .join(DetalleMovimiento, DetalleMovimiento.movimiento_id == Movimiento.id)
            .join(TipoMovimiento, TipoMovimiento.id == Movimiento.tipo_movimiento_id)
            .where(*conditions)
        ).scalar_one()
        statement = (
            select(
                Movimiento.id,
                DetalleMovimiento.id,
                Movimiento.fecha_movimiento,
                Movimiento.creado_en,
                TipoMovimiento.codigo,
                TipoMovimiento.nombre,
                TipoMovimiento.naturaleza,
                Producto.id,
                Producto.codigo,
                Producto.nombre,
                DetalleMovimiento.signo,
                DetalleMovimiento.cantidad,
                DetalleMovimiento.stock_anterior,
                DetalleMovimiento.stock_resultante,
                DetalleMovimiento.precio_unitario,
                Usuario.username,
                Movimiento.motivo,
                Movimiento.documento_referencia,
                Movimiento.movimiento_origen_id,
                Movimiento.importacion_id,
            )
            .select_from(Movimiento)
            .join(DetalleMovimiento, DetalleMovimiento.movimiento_id == Movimiento.id)
            .join(TipoMovimiento, TipoMovimiento.id == Movimiento.tipo_movimiento_id)
            .join(Producto, Producto.id == DetalleMovimiento.producto_id)
            .join(Usuario, Usuario.id == Movimiento.usuario_id)
            .where(*conditions)
            .order_by(Movimiento.id.desc(), DetalleMovimiento.id)
        )
        if page_size > 0:
            statement = statement.limit(page_size).offset((max(page, 1) - 1) * page_size)
        items = [MovementRow(*row) for row in self._session.execute(statement)]
        return Page(items=items, total=int(total), page=max(page, 1), page_size=page_size)

    def has_compensation(self, movement_id: int) -> bool:
        statement = select(Movimiento.id).where(Movimiento.movimiento_origen_id == movement_id)
        return self._session.execute(statement.limit(1)).first() is not None

    def consistency_violations(self) -> list[int]:
        rows = self._session.execute(
            text(
                "SELECT i.producto_id FROM inventario i "
                "LEFT JOIN (SELECT producto_id, SUM(signo*cantidad) AS s "
                "FROM detalle_movimiento GROUP BY producto_id) m "
                "ON m.producto_id = i.producto_id "
                "WHERE i.cantidad <> COALESCE(m.s, 0)"
            )
        ).all()
        return [int(row[0]) for row in rows]


class SqlAlchemyAuditRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(
        self,
        *,
        user_id: int | None,
        username: str | None,
        action: str,
        entity: str,
        entity_id: str | None,
        previous: str | None,
        new: str | None,
        detail: str | None,
        station: str | None,
    ) -> None:
        self._session.add(
            Auditoria(
                fecha_hora=utc_now(),
                usuario_id=user_id,
                username=username,
                accion=action,
                entidad=entity,
                entidad_id=entity_id,
                valor_anterior=previous,
                valor_nuevo=new,
                detalle=detail,
                estacion=station,
            )
        )

    def search(
        self, audit_filter: AuditFilter, *, page: int = 1, page_size: int = 100
    ) -> Page[AuditRow]:
        conditions: list[Any] = []
        if audit_filter.fecha_desde is not None:
            conditions.append(Auditoria.fecha_hora >= f"{audit_filter.fecha_desde.isoformat()}T00:00:00Z")
        if audit_filter.fecha_hasta is not None:
            conditions.append(Auditoria.fecha_hora <= f"{audit_filter.fecha_hasta.isoformat()}T23:59:59Z")
        if audit_filter.username.strip():
            conditions.append(Auditoria.username.contains(audit_filter.username.strip(), autoescape=True))
        if audit_filter.entidad.strip():
            conditions.append(Auditoria.entidad == audit_filter.entidad.strip())
        if audit_filter.accion.strip():
            conditions.append(Auditoria.accion == audit_filter.accion.strip())
        total = self._session.execute(
            select(func.count(Auditoria.id)).where(*conditions)
        ).scalar_one()
        statement = select(Auditoria).where(*conditions).order_by(Auditoria.id.desc())
        if page_size > 0:
            statement = statement.limit(page_size).offset((max(page, 1) - 1) * page_size)
        items = [
            AuditRow(
                id=row.id,
                fecha_hora=row.fecha_hora,
                usuario_id=row.usuario_id,
                username=row.username,
                accion=row.accion,
                entidad=row.entidad,
                entidad_id=row.entidad_id,
                valor_anterior=row.valor_anterior,
                valor_nuevo=row.valor_nuevo,
                detalle=row.detalle,
                estacion=row.estacion,
            )
            for row in self._session.execute(statement).scalars()
        ]
        return Page(items=items, total=int(total), page=max(page, 1), page_size=page_size)
