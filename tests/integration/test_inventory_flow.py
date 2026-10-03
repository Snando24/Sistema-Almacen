"""Catálogos, productos y movimientos con SQLite real."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from sisalmacen.domain.errors import (
    BusinessRuleViolation,
    ConflictError,
    PermissionDenied,
    ValidationError,
)
from sisalmacen.domain.inventory import (
    ALERT_BAJO_MINIMO,
    ALERT_SIN_STOCK,
    AuditFilter,
    MovementFilter,
    MovementLine,
    MovementRequest,
    ProductData,
    ProductFilter,
)

D = Decimal
TODAY = date(2026, 1, 15)


def test_product_without_external_code_gets_a_legacy_identifier(services) -> None:  # type: ignore[no-untyped-def]
    category_id = services.catalogs.list_entries("categoria")[0]["id"]
    unit_id = services.catalogs.list_entries("unidad_medida")[0]["id"]

    product_id = services.products.create(
        ProductData(
            codigo="", nombre="Producto legado", categoria_id=category_id, unidad_id=unit_id
        )
    )

    assert services.products.get(product_id).codigo.startswith("LEGACY-")


def _entry(services, code: str, product_id: int, qty: str, unit_price=None) -> None:  # type: ignore[no-untyped-def]
    services.movements.register(
        MovementRequest(
            tipo_codigo=code,
            fecha=TODAY,
            lines=(MovementLine(product_id, D(qty), unit_price),),
        )
    )


def _stock(services, product_id: int) -> Decimal:  # type: ignore[no-untyped-def]
    return services.products.get(product_id).cantidad


# ---------- catálogos ----------


def test_catalog_crud_unique_and_in_use(services, make_product) -> None:  # type: ignore[no-untyped-def]
    category_id = services.catalogs.create("categoria", {"nombre": "Ferretería"})
    with pytest.raises(ConflictError) as duplicate:
        services.catalogs.create("categoria", {"nombre": "ferretería"})
    assert duplicate.value.code == "CATALOGO_DUPLICADO"

    make_product("P-1")
    with pytest.raises(BusinessRuleViolation) as in_use:
        services.catalogs.set_active("categoria", category_id, active=False)
    assert in_use.value.code == "CATALOGO_EN_USO"

    empty_id = services.catalogs.create("marca", {"nombre": "Acme"})
    services.catalogs.set_active("marca", empty_id, active=False)
    assert services.catalogs.list_entries("marca", include_inactive=False) == []


def test_location_hierarchy_rejects_cycles(services) -> None:  # type: ignore[no-untyped-def]
    parent = services.catalogs.create("ubicacion", {"codigo": "A", "nombre": "Almacén A"})
    child = services.catalogs.create(
        "ubicacion", {"codigo": "A-1", "nombre": "Estante 1", "padre_id": parent}
    )
    with pytest.raises(ValidationError) as cycle:
        services.catalogs.update(
            "ubicacion", parent, {"codigo": "A", "nombre": "Almacén A", "padre_id": child}
        )
    assert cycle.value.code == "UBICACION_CICLO"


# ---------- productos ----------


def test_product_rules(services, make_product) -> None:  # type: ignore[no-untyped-def]
    product_id = make_product("P-1", codigo_barras="777")
    with pytest.raises(ConflictError) as dup_code:
        make_product("p-1")
    assert dup_code.value.code == "PRODUCTO_CODIGO_DUPLICADO"
    with pytest.raises(ConflictError) as dup_barcode:
        make_product("P-2", codigo_barras="777")
    assert dup_barcode.value.code == "PRODUCTO_BARRAS_DUPLICADO"
    with pytest.raises(BusinessRuleViolation) as bad_range:
        make_product("P-3", stock_minimo=D(10), stock_maximo=D(5))
    assert bad_range.value.code == "STOCK_MAXIMO_MENOR_MINIMO"

    # El código de barras queda libre al desactivar y la reactivación se valida (RB-06).
    services.products.deactivate(product_id)
    other = make_product("P-4", codigo_barras="777")
    with pytest.raises(ConflictError):
        services.products.reactivate(product_id)
    services.products.deactivate(other)
    services.products.reactivate(product_id)
    assert services.products.get(product_id).activo


def test_update_increments_row_version_and_audits_old_and_new(services, make_product) -> None:  # type: ignore[no-untyped-def]
    product_id = make_product("P-1")
    record = services.products.get(product_id)
    data = record.as_data()
    data.nombre = "Nombre nuevo"
    services.products.update(product_id, data)

    updated = services.products.get(product_id)
    assert updated.row_version == record.row_version + 1
    entries = services.audit.search(AuditFilter(accion="EDITAR", entidad="producto")).items
    assert entries
    assert "Nombre nuevo" in (entries[0].valor_nuevo or "")
    assert "Producto P-1" in (entries[0].valor_anterior or "")


def test_unit_cannot_change_after_movements(services, make_product) -> None:  # type: ignore[no-untyped-def]
    product_id = make_product("P-1")
    _entry(services, "ENT_COMPRA", product_id, "5")
    data = services.products.get(product_id).as_data()
    kg = next(
        u["id"] for u in services.catalogs.list_entries("unidad_medida") if u["codigo"] == "KG"
    )
    data.unidad_id = kg
    with pytest.raises(BusinessRuleViolation) as error:
        services.products.update(product_id, data)
    assert error.value.code == "UNIDAD_CON_MOVIMIENTOS"


def test_search_by_text_filters_and_paging(services, make_product) -> None:  # type: ignore[no-untyped-def]
    for index in range(7):
        make_product(f"A-{index}", codigo_barras=f"99{index}")
    inactive = make_product("B-1")
    services.products.deactivate(inactive)

    page = services.products.search(ProductFilter(texto="a-"), page=2, page_size=3)
    assert page.total == 7
    assert len(page.items) == 3
    assert page.pages == 3
    by_barcode = services.products.search(ProductFilter(texto="993"))
    assert [p.codigo for p in by_barcode.items] == ["A-3"]
    assert services.products.search(ProductFilter(estado="INACTIVO")).total == 1
    assert services.products.search(ProductFilter(estado=None)).total == 8


# ---------- movimientos ----------


def test_entry_and_exit_update_stock_and_history(services, make_product) -> None:  # type: ignore[no-untyped-def]
    product_id = make_product("P-1")
    _entry(services, "ENT_COMPRA", product_id, "10")
    _entry(services, "SAL_CONSUMO", product_id, "4")

    assert _stock(services, product_id) == D("6")
    history = services.movements.history(MovementFilter(producto_id=product_id)).items
    assert [(r.signo, r.stock_anterior, r.stock_resultante) for r in history] == [
        (-1, D("10"), D("6")),
        (1, D("0"), D("10")),
    ]
    assert services.movements.verify_consistency() == []


def test_exit_without_stock_is_rejected_and_nothing_persists(services, make_product) -> None:  # type: ignore[no-untyped-def]
    first = make_product("P-1")
    second = make_product("P-2")
    _entry(services, "ENT_COMPRA", first, "5")
    before = services.movements.history(MovementFilter()).total

    request = MovementRequest(
        tipo_codigo="SAL_CONSUMO",
        fecha=TODAY,
        lines=(MovementLine(first, D("2")), MovementLine(second, D("1"))),
    )
    with pytest.raises(BusinessRuleViolation) as error:
        services.movements.register(request)

    assert error.value.code == "STOCK_INSUFICIENTE"
    assert _stock(services, first) == D("5")  # la primera línea tampoco se aplicó
    assert services.movements.history(MovementFilter()).total == before
    assert services.movements.verify_consistency() == []


def test_negative_stock_allowed_by_setting(services, make_product) -> None:  # type: ignore[no-untyped-def]
    product_id = make_product("P-1")
    services.settings.update({"inventario.permitir_stock_negativo": "1"})
    _entry(services, "SAL_CONSUMO", product_id, "2")
    assert _stock(services, product_id) == D("-2")
    assert services.movements.verify_consistency() == []


def test_decimal_rules_follow_unit(services, make_product) -> None:  # type: ignore[no-untyped-def]
    units = make_product("U-1", unit="UND")
    meters = make_product("M-1", unit="MT")
    with pytest.raises(ValidationError) as whole:
        _entry(services, "ENT_COMPRA", units, "1.5")
    assert whole.value.code == "CANTIDAD_INVALIDA"
    for bad in ("0", "-1"):
        with pytest.raises(ValidationError):
            _entry(services, "ENT_COMPRA", meters, bad)
    _entry(services, "ENT_COMPRA", meters, "1.5")
    assert _stock(services, meters) == D("1.5")


def test_inactive_product_cannot_move(services, make_product) -> None:  # type: ignore[no-untyped-def]
    product_id = make_product("P-1")
    services.products.deactivate(product_id)
    with pytest.raises(ConflictError) as error:
        _entry(services, "ENT_COMPRA", product_id, "1")
    assert error.value.code == "PRODUCTO_INACTIVO"


def test_adjustment_requires_reason_and_computes_difference(services, make_product) -> None:  # type: ignore[no-untyped-def]
    product_id = make_product("P-1")
    _entry(services, "ENT_COMPRA", product_id, "10")
    with pytest.raises(ValidationError) as missing:
        services.movements.adjust_to_count(product_id, D("7"), "  ")
    assert missing.value.code == "MOTIVO_REQUERIDO"

    result = services.movements.adjust_to_count(product_id, D("7"), "Conteo físico")
    assert result is not None
    assert _stock(services, product_id) == D("7")
    assert services.movements.adjust_to_count(product_id, D("7"), "Conteo físico") is None
    assert services.movements.verify_consistency() == []


def test_type_requiring_reason_is_enforced(services, make_product) -> None:  # type: ignore[no-untyped-def]
    product_id = make_product("P-1")
    _entry(services, "ENT_COMPRA", product_id, "3")
    with pytest.raises(ValidationError) as error:
        _entry(services, "SAL_PERDIDA", product_id, "1")
    assert error.value.code == "MOTIVO_REQUERIDO"


def test_compensating_correction_keeps_original_and_links(services, make_product) -> None:  # type: ignore[no-untyped-def]
    product_id = make_product("P-1")
    _entry(services, "ENT_COMPRA", product_id, "10")
    original = services.movements.history(MovementFilter(producto_id=product_id)).items[0]

    result = services.movements.correct(original.movimiento_id, "Error de digitación")

    assert _stock(services, product_id) == D("0")
    rows = services.movements.history(MovementFilter(producto_id=product_id)).items
    assert len(rows) == 2
    assert rows[0].movimiento_origen_id == original.movimiento_id
    assert rows[0].movimiento_id == result.movimiento_id
    with pytest.raises(ConflictError) as again:
        services.movements.correct(original.movimiento_id, "Otra vez")
    assert again.value.code == "MOVIMIENTO_YA_CORREGIDO"
    assert services.movements.verify_consistency() == []


def test_movement_types_admin(services) -> None:  # type: ignore[no-untyped-def]
    type_id = services.movements.create_type(
        "ENT_DONACION", "Donación", "ENTRADA", requires_reason=False
    )
    services.movements.set_type_active(type_id, active=False)
    assert all(
        t.codigo != "ENT_DONACION" for t in services.movements.list_types(include_inactive=False)
    )
    system_type = next(t for t in services.movements.list_types() if t.es_sistema)
    with pytest.raises(BusinessRuleViolation) as error:
        services.movements.set_type_active(system_type.id, active=False)
    assert error.value.code == "TIPO_SISTEMA"


def test_alerts_and_dashboard(services, make_product) -> None:  # type: ignore[no-untyped-def]
    empty = make_product("E-1")
    low = make_product("L-1", stock_minimo=D(5), stock_maximo=D(10))
    over = make_product("O-1", stock_minimo=D(1), stock_maximo=D(10))
    _entry(services, "ENT_COMPRA", low, "5", D("2.5"))
    _entry(services, "ENT_COMPRA", over, "11", D("1"))

    def codes(alert: str) -> list[str]:
        return [p.codigo for p in services.products.search(ProductFilter(alerta=alert)).items]

    assert codes(ALERT_SIN_STOCK) == ["E-1"]
    assert codes(ALERT_BAJO_MINIMO) == ["L-1"]
    assert codes("SOBRE_MAXIMO") == ["O-1"]
    assert sorted(codes("CUALQUIERA")) == ["E-1", "L-1", "O-1"]
    assert empty

    snapshot = services.load_dashboard()
    assert (snapshot.productos_sin_stock, snapshot.productos_bajo_minimo) == (1, 1)
    assert snapshot.productos_sobre_maximo == 1
    assert snapshot.entradas_hoy >= 0


def test_permissions_are_enforced_in_use_cases(app_context, services, make_product) -> None:  # type: ignore[no-untyped-def]
    from dataclasses import replace

    from sisalmacen.application.catalogs import CatalogService
    from sisalmacen.application.products import ProductService
    from sisalmacen.infrastructure.db.uow import SqlAlchemyUnitOfWork

    make_product("P-1")
    reader = replace(
        services.session, permisos={"productos.ver", "catalogos.ver"}, rol_codigo="CONSULTA"
    )

    def factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(app_context.session_factory)

    products = ProductService(factory, reader)  # type: ignore[arg-type]
    catalogs = CatalogService(factory, reader)  # type: ignore[arg-type]

    assert products.search(ProductFilter()).total == 1
    with pytest.raises(PermissionDenied):
        products.create(ProductData(codigo="X", nombre="X", categoria_id=1, unidad_id=1))
    with pytest.raises(PermissionDenied):
        catalogs.create("marca", {"nombre": "No"})
