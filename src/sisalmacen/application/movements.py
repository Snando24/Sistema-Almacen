"""Registro de movimientos de inventario: único punto que modifica el stock (RB, ADR-14)."""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal

from sisalmacen.application.auditing import AuditRecorder
from sisalmacen.application.auth import AuthorizationService, CurrentSession
from sisalmacen.application.ports import WorkUnit, WorkUnitFactory
from sisalmacen.application.settings import flag
from sisalmacen.domain.errors import (
    BusinessRuleViolation,
    ConflictError,
    NotFoundError,
    PermissionDenied,
    ValidationError,
)
from sisalmacen.domain.inventory import (
    NATURE_SIGN,
    QUANTITY_PLACES,
    ZERO,
    MovementFilter,
    MovementLine,
    MovementRequest,
    MovementRow,
    MovementType,
    Page,
    RegisteredMovement,
    decimal_places,
    is_whole,
)

_PERMISSION_BY_NATURE = {
    "ENTRADA": "movimientos.entrada",
    "SALIDA": "movimientos.salida",
    "AJUSTE_POS": "movimientos.ajuste",
    "AJUSTE_NEG": "movimientos.ajuste",
}
_ACTION_BY_NATURE = {
    "ENTRADA": "ENTRADA",
    "SALIDA": "SALIDA",
    "AJUSTE_POS": "AJUSTE",
    "AJUSTE_NEG": "AJUSTE",
}
_TYPE_CODE = re.compile(r"^[A-Z0-9_]{2,30}$")


def today_local() -> date:
    return datetime.now().astimezone().date()


class MovementService:
    """Entradas, salidas, ajustes, correcciones e historial."""

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

    # ----- registro -----

    def register(self, request: MovementRequest) -> RegisteredMovement:
        """Registra un movimiento completo en una sola transacción."""

        with self._uow_factory() as uow:
            result = self.register_in(uow, request)
            uow.commit()
        return result

    def register_in(
        self,
        uow: WorkUnit,
        request: MovementRequest,
        *,
        check_permission: bool = True,
    ) -> RegisteredMovement:
        """Inserta movimiento, detalles, stock y auditoría sin confirmar la transacción."""

        movement_type = uow.movements.get_type(request.tipo_codigo)
        if movement_type is None or not movement_type.activo:
            raise ValidationError(
                "El tipo de movimiento no es válido.", code="TIPO_MOVIMIENTO_INVALIDO"
            )
        if check_permission:
            self._authz.require_permission(
                self._actor, _PERMISSION_BY_NATURE[movement_type.naturaleza]
            )
        if not request.lines:
            raise ValidationError(
                "Debe agregar al menos un producto.", code="MOVIMIENTO_SIN_LINEAS"
            )
        reason = (request.motivo or "").strip() or None
        if (movement_type.requiere_motivo or movement_type.naturaleza.startswith("AJUSTE")) and (
            reason is None
        ):
            raise ValidationError("Debe indicar el motivo.", code="MOTIVO_REQUERIDO")

        uow.begin_immediate()
        settings = uow.settings.get_all()
        allow_negative = flag(settings, "inventario.permitir_stock_negativo")
        sign = NATURE_SIGN[movement_type.naturaleza]

        movement_id = uow.movements.add_movement(
            type_id=movement_type.id,
            movement_date=request.fecha,
            user_id=self._actor.user_id,
            reason=reason,
            reference=(request.documento_referencia or "").strip() or None,
            note=(request.observacion or "").strip() or None,
            import_id=request.importacion_id,
            origin_id=request.movimiento_origen_id,
        )

        results: list[tuple[int, Decimal, Decimal]] = []
        audit_lines: list[dict[str, str]] = []
        negative = False
        for line in request.lines:
            previous, resulting = self._apply_line(
                uow, movement_id, line, sign, allow_negative=allow_negative
            )
            negative = negative or resulting < ZERO
            results.append((line.producto_id, previous, resulting))
            audit_lines.append(
                {
                    "producto_id": str(line.producto_id),
                    "cantidad": format(line.cantidad, "f"),
                    "stock_anterior": format(previous, "f"),
                    "stock_resultante": format(resulting, "f"),
                }
            )

        self._audit.record(
            uow,
            _ACTION_BY_NATURE[movement_type.naturaleza],
            "movimiento",
            movement_id,
            new={
                "tipo": movement_type.codigo,
                "fecha": request.fecha,
                "motivo": reason,
                "origen": request.movimiento_origen_id,
                "importacion": request.importacion_id,
                "stock_negativo": negative,
                "lineas": audit_lines,
            },
        )
        return RegisteredMovement(movimiento_id=movement_id, lines=tuple(results))

    def _apply_line(
        self,
        uow: WorkUnit,
        movement_id: int,
        line: MovementLine,
        sign: int,
        *,
        allow_negative: bool,
    ) -> tuple[Decimal, Decimal]:
        product = uow.products.get(line.producto_id)
        if product is None:
            raise NotFoundError("No se encontró el producto.", code="PRODUCTO_NO_ENCONTRADO")
        if not product.activo:
            raise ConflictError(
                f"El producto {product.codigo} está inactivo.", code="PRODUCTO_INACTIVO"
            )
        quantity = line.cantidad
        if (
            quantity <= ZERO
            or decimal_places(quantity) > QUANTITY_PLACES
            or (not product.unidad_permite_decimales and not is_whole(quantity))
        ):
            raise ValidationError(
                "La cantidad debe ser mayor que cero y respetar los decimales de la unidad.",
                code="CANTIDAD_INVALIDA",
            )

        previous = uow.movements.get_stock(line.producto_id)
        resulting = previous + sign * quantity
        if resulting < ZERO and not allow_negative:
            raise BusinessRuleViolation(
                f"Stock insuficiente de {product.codigo}: disponible {previous:f}, "
                f"solicitado {quantity:f}.",
                code="STOCK_INSUFICIENTE",
            )
        uow.movements.add_detail(
            movement_id=movement_id,
            product_id=line.producto_id,
            sign=sign,
            quantity=quantity,
            previous=previous,
            resulting=resulting,
            unit_price=line.precio_unitario,
        )
        uow.movements.set_stock(line.producto_id, resulting)
        return previous, resulting

    def adjust_to_count(
        self,
        product_id: int,
        counted: Decimal,
        reason: str,
        *,
        movement_date: date | None = None,
    ) -> RegisteredMovement | None:
        """Ajusta al stock contado; devuelve `None` si no hay diferencia."""

        self._authz.require_permission(self._actor, "movimientos.ajuste")
        if counted < ZERO:
            raise ValidationError("El stock contado no puede ser negativo.", code="CANTIDAD_INVALIDA")
        with self._uow_factory() as uow:
            current = uow.movements.get_stock(product_id)
            difference = counted - current
            if difference == ZERO:
                return None
            request = MovementRequest(
                tipo_codigo="AJ_POSITIVO" if difference > ZERO else "AJ_NEGATIVO",
                fecha=movement_date or today_local(),
                lines=(MovementLine(product_id, abs(difference)),),
                motivo=reason,
            )
            result = self.register_in(uow, request)
            uow.commit()
        return result

    def correct(self, movement_id: int, reason: str) -> RegisteredMovement:
        """Genera un movimiento compensatorio enlazado; el original no se modifica (ADR-13)."""

        self._authz.require_permission(self._actor, "movimientos.ajuste")
        if self._actor.rol_codigo != "ADMIN":
            raise PermissionDenied(
                "Solo un administrador puede corregir movimientos.", code="SIN_PERMISO"
            )
        with self._uow_factory() as uow:
            rows = uow.movements.search(
                MovementFilter(movimiento_id=movement_id), page=1, page_size=0
            ).items
            if not rows:
                raise NotFoundError("No se encontró el movimiento.", code="MOVIMIENTO_NO_ENCONTRADO")
            if rows[0].movimiento_origen_id is not None:
                raise BusinessRuleViolation(
                    "Un movimiento de corrección no puede corregirse de nuevo.",
                    code="MOVIMIENTO_ES_CORRECCION",
                )
            if uow.movements.has_compensation(movement_id):
                raise ConflictError(
                    "El movimiento ya fue corregido.", code="MOVIMIENTO_YA_CORREGIDO"
                )
            request = MovementRequest(
                tipo_codigo="AJ_NEGATIVO" if rows[0].signo > 0 else "AJ_POSITIVO",
                fecha=today_local(),
                lines=tuple(MovementLine(row.producto_id, row.cantidad) for row in rows),
                motivo=reason,
                documento_referencia=f"Corrección de movimiento #{movement_id}",
                movimiento_origen_id=movement_id,
            )
            result = self.register_in(uow, request)
            uow.commit()
        return result

    # ----- consultas -----

    def history(
        self, movement_filter: MovementFilter, *, page: int = 1, page_size: int = 100
    ) -> Page[MovementRow]:
        self._authz.require_permission(self._actor, "inventario.ver")
        with self._uow_factory() as uow:
            return uow.movements.search(movement_filter, page=page, page_size=page_size)

    def list_types(self, *, include_inactive: bool = True) -> list[MovementType]:
        with self._uow_factory() as uow:
            return uow.movements.list_types(include_inactive=include_inactive)

    def verify_consistency(self) -> list[int]:
        """Productos cuyo stock no coincide con la suma de sus movimientos (RN-003)."""

        with self._uow_factory() as uow:
            return uow.movements.consistency_violations()

    # ----- tipos de movimiento (HU-04.5) -----

    def create_type(self, code: str, name: str, nature: str, *, requires_reason: bool) -> int:
        self._authz.require_permission(self._actor, "configuracion.gestionar")
        code = code.strip().upper()
        name = name.strip()
        if not _TYPE_CODE.match(code):
            raise ValidationError(
                "El código debe tener 2 a 30 letras mayúsculas, números o guion bajo.",
                code="TIPO_CODIGO_INVALIDO",
            )
        if not name:
            raise ValidationError("Debe indicar el nombre.", code="TIPO_NOMBRE_REQUERIDO")
        if nature not in NATURE_SIGN:
            raise ValidationError("Naturaleza no válida.", code="TIPO_NATURALEZA_INVALIDA")
        with self._uow_factory() as uow:
            if uow.movements.get_type(code) is not None:
                raise ConflictError("Ya existe ese tipo de movimiento.", code="TIPO_DUPLICADO")
            type_id = uow.movements.add_type(code, name, nature, requires_reason=requires_reason)
            self._audit.record(
                uow,
                "CREAR",
                "tipo_movimiento",
                type_id,
                new={"codigo": code, "nombre": name, "naturaleza": nature},
            )
            uow.commit()
        return type_id

    def update_type(self, type_id: int, name: str, *, requires_reason: bool) -> None:
        self._authz.require_permission(self._actor, "configuracion.gestionar")
        name = name.strip()
        if not name:
            raise ValidationError("Debe indicar el nombre.", code="TIPO_NOMBRE_REQUERIDO")
        with self._uow_factory() as uow:
            current = _find_type(uow, type_id)
            uow.movements.update_type(type_id, name, requires_reason=requires_reason)
            self._audit.record(
                uow,
                "EDITAR",
                "tipo_movimiento",
                type_id,
                previous={"nombre": current.nombre, "requiere_motivo": current.requiere_motivo},
                new={"nombre": name, "requiere_motivo": requires_reason},
            )
            uow.commit()

    def set_type_active(self, type_id: int, *, active: bool) -> None:
        self._authz.require_permission(self._actor, "configuracion.gestionar")
        with self._uow_factory() as uow:
            current = _find_type(uow, type_id)
            if not active and current.es_sistema:
                raise BusinessRuleViolation(
                    "Los tipos de sistema no se pueden desactivar.", code="TIPO_SISTEMA"
                )
            uow.movements.set_type_active(type_id, active=active)
            self._audit.record(
                uow,
                "ACTIVAR" if active else "DESACTIVAR",
                "tipo_movimiento",
                type_id,
                previous={"activo": current.activo},
                new={"activo": active},
            )
            uow.commit()


def _find_type(uow: WorkUnit, type_id: int) -> MovementType:
    for movement_type in uow.movements.list_types(include_inactive=True):
        if movement_type.id == type_id:
            return movement_type
    raise NotFoundError("No se encontró el tipo de movimiento.", code="TIPO_NO_ENCONTRADO")
