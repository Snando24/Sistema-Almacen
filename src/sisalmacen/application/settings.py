"""Configuración del sistema (HU-08.2)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from sisalmacen.application.auditing import AuditRecorder
from sisalmacen.application.auth import AuthorizationService, CurrentSession
from sisalmacen.application.ports import WorkUnitFactory
from sisalmacen.domain.errors import ValidationError


@dataclass(frozen=True)
class SettingSpec:
    key: str
    label: str
    kind: str  # text | bool | int | folder | file | choice
    group: str
    choices: tuple[tuple[str, str], ...] = ()


SETTING_SPECS: tuple[SettingSpec, ...] = (
    SettingSpec("empresa.nombre", "Nombre de la empresa", "text", "Empresa"),
    SettingSpec("empresa.documento", "RUC (opcional)", "text", "Empresa"),
    SettingSpec("empresa.direccion", "Dirección", "text", "Empresa"),
    SettingSpec("empresa.telefono", "Teléfono", "text", "Empresa"),
    SettingSpec("empresa.logo_ruta", "Logo para reportes", "file", "Empresa"),
    SettingSpec("moneda.codigo", "Moneda", "text", "Inventario"),
    SettingSpec(
        "inventario.permitir_stock_negativo", "Permitir stock negativo", "bool", "Inventario"
    ),
    SettingSpec(
        "inventario.usar_precios", "Gestionar precios y valorización", "bool", "Inventario"
    ),
    SettingSpec("importacion.max_filas", "Máximo de filas por CSV", "int", "Importación"),
    SettingSpec("backup.carpeta", "Carpeta de respaldos", "folder", "Respaldos"),
    SettingSpec("backup.recordatorio_dias", "Días para recordar respaldo", "int", "Respaldos"),
    SettingSpec(
        "ui.tema",
        "Tema visual",
        "choice",
        "Apariencia",
        (("claro", "Modo claro"), ("oscuro", "Modo oscuro")),
    ),
)
_SPEC_BY_KEY = {spec.key: spec for spec in SETTING_SPECS}


def flag(settings: dict[str, str], key: str, *, default: bool = False) -> bool:
    """Interpreta una configuración booleana ('1'/'0')."""

    value = settings.get(key)
    if value is None or value == "":
        return default
    return value.strip() == "1"


def int_setting(settings: dict[str, str], key: str, default: int) -> int:
    try:
        return int(settings.get(key, "") or default)
    except ValueError:
        return default


class SettingsService:
    """Lectura y modificación auditada de parámetros."""

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

    def read_all(self) -> dict[str, str]:
        """Lectura interna sin permiso especial: la usan pantallas y reportes."""

        with self._uow_factory() as uow:
            return uow.settings.get_all()

    def update(self, values: dict[str, str]) -> None:
        self._authz.require_permission(self._actor, "configuracion.gestionar")
        clean: dict[str, str] = {}
        for key, raw in values.items():
            spec = _SPEC_BY_KEY.get(key)
            if spec is None:
                raise ValidationError(f"Parámetro desconocido: {key}.", code="CONFIG_DESCONOCIDA")
            value = str(raw).strip()
            if spec.kind == "bool":
                value = "1" if value in ("1", "true", "True") else "0"
            elif spec.kind == "int":
                if not value.isdigit() or int(value) <= 0:
                    raise ValidationError(
                        f"{spec.label}: debe ser un entero positivo.", code="CONFIG_VALOR_INVALIDO"
                    )
            elif spec.kind == "choice" and value not in {option[0] for option in spec.choices}:
                raise ValidationError(
                    f"{spec.label}: valor no permitido.", code="CONFIG_VALOR_INVALIDO"
                )
            elif spec.key == "empresa.nombre" and not value:
                raise ValidationError(
                    "Debe indicar el nombre de la empresa.", code="EMPRESA_NOMBRE_REQUERIDO"
                )
            clean[key] = value

        with self._uow_factory() as uow:
            current = uow.settings.get_all()
            changed = {k: v for k, v in clean.items() if current.get(k, "") != v}
            if not changed:
                return
            uow.settings.set_many(changed)
            self._audit.record(
                uow,
                "CONFIGURAR",
                "configuracion",
                None,
                previous={k: current.get(k, "") for k in changed},
                new=changed,
            )
            uow.commit()

    def mark_backup_done(self) -> None:
        """Guarda la fecha del último respaldo; el servicio de respaldo lo audita."""

        stamp = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        with self._uow_factory() as uow:
            uow.settings.set_many({"backup.ultimo": stamp})
            uow.commit()
