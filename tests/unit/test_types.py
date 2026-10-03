"""Pruebas de TypeDecorator para decimales escalados."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Column, Integer, MetaData, Table, create_engine, select, text

from sisalmacen.infrastructure.db.types import ScaledMoney, ScaledQuantity


def test_scaled_decimal_round_trip_preserves_precision() -> None:
    metadata = MetaData()
    medicion = Table(
        "medicion",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("cantidad", ScaledQuantity(), nullable=False),
        Column("monto", ScaledMoney(), nullable=False),
    )
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    metadata.create_all(engine)

    with engine.begin() as connection:
        connection.execute(
            medicion.insert().values(
                cantidad=Decimal("0.001"),
                monto=Decimal("0.0001"),
            )
        )
        fila_tipada = connection.execute(select(medicion.c.cantidad, medicion.c.monto)).one()
        fila_cruda = connection.execute(text("SELECT cantidad, monto FROM medicion")).one()

    assert fila_tipada.cantidad == Decimal("0.001")
    assert fila_tipada.monto == Decimal("0.0001")
    assert fila_cruda.cantidad == 1
    assert fila_cruda.monto == 1
