"""Repositorios SQLAlchemy de catálogos y productos."""

from __future__ import annotations


from collections.abc import Mapping

from datetime import UTC, datetime

from decimal import Decimal

from typing import Any


from sqlalchemy import Select, and_, false, func, or_, select

from sqlalchemy.orm import Session


from sisalmacen.domain.inventory import (
    ALERT_AGOTADO,
    ALERT_BAJO_MINIMO,
    ALERT_CUALQUIERA,
    ZERO,
    Page,
    ProductData,
    ProductFilter,
    ProductRecord,
    normalize_alert_code,
)

from sisalmacen.infrastructure.db.models import (
    Categoria,
    DetalleMovimiento,
    Inventario,
    Marca,
    Producto,
    Proveedor,
    Ubicacion,
    UnidadMedida,
)


_CATALOG_MODELS: dict[str, Any] = {
    "categoria": Categoria,
    "marca": Marca,
    "unidad_medida": UnidadMedida,
    "proveedor": Proveedor,
    "ubicacion": Ubicacion,
}

_PRODUCT_FK = {
    "categoria": Producto.categoria_id,
    "marca": Producto.marca_id,
    "unidad_medida": Producto.unidad_id,
    "proveedor": Producto.proveedor_id,
    "ubicacion": Producto.ubicacion_id,
}


def utc_now() -> str:

    return datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _db_value(value: Any) -> Any:

    return int(value) if isinstance(value, bool) else value


class SqlAlchemyCatalogRepository:
    def __init__(self, session: Session) -> None:

        self._session = session

    def _model(self, kind: str) -> Any:

        return _CATALOG_MODELS[kind]

    @staticmethod
    def _to_dict(entry: Any) -> dict[str, Any]:

        return {column.name: getattr(entry, column.name) for column in entry.__table__.columns}

    def list_entries(self, kind: str, *, include_inactive: bool = True) -> list[dict[str, Any]]:

        model = self._model(kind)

        statement = select(model).order_by(func.lower(model.nombre))

        if not include_inactive:
            statement = statement.where(model.activo == 1)

        return [self._to_dict(row) for row in self._session.execute(statement).scalars()]

    def get(self, kind: str, entry_id: int) -> dict[str, Any] | None:

        entry = self._session.get(self._model(kind), entry_id)

        return None if entry is None else self._to_dict(entry)

    def find(
        self, kind: str, field: str, value: str, *, exclude_id: int | None = None
    ) -> dict[str, Any] | None:

        model = self._model(kind)

        statement = select(model).where(func.lower(getattr(model, field)) == value.strip().lower())

        if exclude_id is not None:
            statement = statement.where(model.id != exclude_id)

        entry = self._session.execute(statement.limit(1)).scalar_one_or_none()

        return None if entry is None else self._to_dict(entry)

    def add(self, kind: str, data: Mapping[str, Any]) -> int:

        entry = self._model(kind)(**{key: _db_value(value) for key, value in data.items()})

        self._session.add(entry)

        self._session.flush()

        return int(entry.id)

    def update(self, kind: str, entry_id: int, data: Mapping[str, Any]) -> None:

        entry = self._session.get(self._model(kind), entry_id)

        if entry is None:
            raise RuntimeError("Registro de catálogo inexistente.")

        for key, value in data.items():
            setattr(entry, key, _db_value(value))

        entry.row_version += 1

        self._session.flush()

    def set_active(self, kind: str, entry_id: int, *, active: bool) -> None:

        entry = self._session.get(self._model(kind), entry_id)

        if entry is None:
            raise RuntimeError("Registro de catálogo inexistente.")

        entry.activo = 1 if active else 0

        entry.row_version += 1

        self._session.flush()

    def count_active_products_using(self, kind: str, entry_id: int) -> int:

        statement = select(func.count(Producto.id)).where(
            _PRODUCT_FK[kind] == entry_id, Producto.activo == 1
        )

        return int(self._session.execute(statement).scalar_one())


def _record_select() -> Select[Any]:

    return (
        select(
            Producto,
            Inventario.cantidad,
            Categoria.nombre,
            UnidadMedida.codigo,
            UnidadMedida.permite_decimales,
            Marca.nombre,
            Proveedor.nombre,
            Ubicacion.codigo,
        )
        .select_from(Producto)
        .join(Inventario, Inventario.producto_id == Producto.id)
        .join(Categoria, Categoria.id == Producto.categoria_id)
        .join(UnidadMedida, UnidadMedida.id == Producto.unidad_id)
        .outerjoin(Marca, Marca.id == Producto.marca_id)
        .outerjoin(Proveedor, Proveedor.id == Producto.proveedor_id)
        .outerjoin(Ubicacion, Ubicacion.id == Producto.ubicacion_id)
    )


def _to_record(row: Any) -> ProductRecord:

    product, quantity, category, unit, unit_decimals, brand, supplier, location = row

    return ProductRecord(
        id=product.id,
        codigo=product.codigo,
        nombre=product.nombre,
        categoria_id=product.categoria_id,
        unidad_id=product.unidad_id,
        codigo_barras=product.codigo_barras,
        descripcion=product.descripcion,
        marca_id=product.marca_id,
        proveedor_id=product.proveedor_id,
        ubicacion_id=product.ubicacion_id,
        precio_compra=product.precio_compra,
        precio_venta=product.precio_venta,
        stock_minimo=product.stock_minimo,
        observaciones=product.observaciones,
        activo=bool(product.activo),
        creado_en=product.creado_en,
        actualizado_en=product.actualizado_en,
        row_version=product.row_version,
        cantidad=quantity,
        categoria=category,
        unidad=unit,
        unidad_permite_decimales=bool(unit_decimals),
        marca=brand,
        proveedor=supplier,
        ubicacion=location,
    )


def alert_conditions() -> dict[str, Any]:
    """Condiciones SQL de alertas de inventario."""

    quantity = Inventario.cantidad

    out_of_stock = quantity <= ZERO
    low = and_(
        quantity > ZERO, Producto.stock_minimo.is_not(None), quantity <= Producto.stock_minimo
    )

    conditions: dict[str, Any] = {
        ALERT_AGOTADO: out_of_stock,
        ALERT_BAJO_MINIMO: low,
        ALERT_CUALQUIERA: or_(out_of_stock, low),
    }

    return conditions


def _filter_conditions(product_filter: ProductFilter) -> list[Any]:

    conditions: list[Any] = []

    text = product_filter.texto.strip()

    if text:
        conditions.append(
            or_(
                Producto.codigo.contains(text, autoescape=True),
                Producto.nombre.contains(text, autoescape=True),
                Producto.codigo_barras.contains(text, autoescape=True),
            )
        )

    for column, value in (
        (Producto.categoria_id, product_filter.categoria_id),
        (Producto.marca_id, product_filter.marca_id),
        (Producto.proveedor_id, product_filter.proveedor_id),
        (Producto.ubicacion_id, product_filter.ubicacion_id),
    ):
        if value is not None:
            conditions.append(column == value)

    if product_filter.estado == "ACTIVO":
        conditions.append(Producto.activo == 1)

    elif product_filter.estado == "INACTIVO":
        conditions.append(Producto.activo == 0)

    if product_filter.alerta:
        conditions.append(Producto.activo == 1)

        conditions.append(alert_conditions()[normalize_alert_code(product_filter.alerta)])

    if product_filter.precio_desde is not None:
        conditions.append(Producto.precio_venta >= product_filter.precio_desde)

    if product_filter.precio_hasta is not None:
        conditions.append(Producto.precio_venta <= product_filter.precio_hasta)

    if product_filter.registrado_desde is not None:
        conditions.append(
            Producto.creado_en >= f"{product_filter.registrado_desde.isoformat()}T00:00:00Z"
        )

    if product_filter.registrado_hasta is not None:
        conditions.append(
            Producto.creado_en <= f"{product_filter.registrado_hasta.isoformat()}T23:59:59Z"
        )

    return conditions


class SqlAlchemyProductRepository:
    def __init__(self, session: Session) -> None:

        self._session = session

    def _one(self, *conditions: Any) -> ProductRecord | None:

        row = self._session.execute(_record_select().where(*conditions)).first()

        return None if row is None else _to_record(row)

    def get(self, product_id: int) -> ProductRecord | None:

        return self._one(Producto.id == product_id)

    def get_by_code(self, code: str) -> ProductRecord | None:

        return self._one(func.lower(Producto.codigo) == code.strip().lower())

    def find_active_by_barcode(
        self, barcode: str, *, exclude_id: int | None = None
    ) -> ProductRecord | None:

        conditions = [Producto.codigo_barras == barcode, Producto.activo == 1]

        if exclude_id is not None:
            conditions.append(Producto.id != exclude_id)

        return self._one(*conditions)

    def add(self, data: ProductData, user_id: int) -> int:

        product = Producto(
            codigo=data.codigo,
            codigo_barras=data.codigo_barras,
            nombre=data.nombre,
            descripcion=data.descripcion,
            categoria_id=data.categoria_id,
            unidad_id=data.unidad_id,
            marca_id=data.marca_id,
            proveedor_id=data.proveedor_id,
            ubicacion_id=data.ubicacion_id,
            precio_compra=data.precio_compra,
            precio_venta=data.precio_venta,
            stock_minimo=data.stock_minimo,
            observaciones=data.observaciones,
            activo=1 if data.activo else 0,
            creado_en=utc_now(),
            creado_por=user_id,
            actualizado_en=utc_now(),
            actualizado_por=user_id,
        )

        self._session.add(product)

        self._session.flush()

        return int(product.id)

    def _load(self, product_id: int) -> Producto:

        product = self._session.get(Producto, product_id)

        if product is None:
            raise RuntimeError("Producto inexistente.")

        return product

    def update(self, product_id: int, data: ProductData, user_id: int) -> None:

        product = self._load(product_id)

        for key in (
            "codigo",
            "codigo_barras",
            "nombre",
            "descripcion",
            "categoria_id",
            "unidad_id",
            "marca_id",
            "proveedor_id",
            "ubicacion_id",
            "precio_compra",
            "precio_venta",
            "stock_minimo",
            "observaciones",
        ):
            setattr(product, key, getattr(data, key))

        self._touch(product, user_id)

    def apply_changes(self, product_id: int, changes: Mapping[str, Any], user_id: int) -> None:

        product = self._load(product_id)

        for key, value in changes.items():
            setattr(product, key, _db_value(value))

        self._touch(product, user_id)

    def set_active(self, product_id: int, *, active: bool, user_id: int) -> None:

        product = self._load(product_id)

        product.activo = 1 if active else 0

        self._touch(product, user_id)

    def _touch(self, product: Producto, user_id: int) -> None:

        product.row_version += 1

        product.actualizado_en = utc_now()

        product.actualizado_por = user_id

        self._session.flush()

    def search(
        self, product_filter: ProductFilter, *, page: int = 1, page_size: int = 50
    ) -> Page[ProductRecord]:

        conditions = _filter_conditions(product_filter)

        total = self._session.execute(
            select(func.count())
            .select_from(Producto)
            .join(Inventario, Inventario.producto_id == Producto.id)
            .where(*conditions)
        ).scalar_one()

        statement = _record_select().where(*conditions).order_by(Producto.codigo)

        if page_size > 0:
            statement = statement.limit(page_size).offset((max(page, 1) - 1) * page_size)

        items = [_to_record(row) for row in self._session.execute(statement)]

        return Page(items=items, total=int(total), page=max(page, 1), page_size=page_size)

    def has_movements(self, product_id: int) -> bool:

        statement = (
            select(DetalleMovimiento.id).where(DetalleMovimiento.producto_id == product_id).limit(1)
        )

        return self._session.execute(statement).first() is not None


def money_total(raw: int | None) -> Decimal:
    """Convierte una suma de cantidad×1000 por precio×10000 a Decimal exacto."""

    return Decimal(raw or 0) / Decimal(10**7)
