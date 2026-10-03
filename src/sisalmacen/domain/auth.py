"""Modelos y puertos para autenticación y estado inicial."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass
class AuthUser:
    """Representa un usuario autenticable del sistema."""

    id: int | None
    username: str
    nombre_completo: str
    password_hash: str
    rol_id: int
    rol_codigo: str
    rol_nombre: str
    activo: bool
    debe_cambiar_password: bool
    intentos_fallidos: int
    bloqueado_hasta: str | None
    ultimo_login: str | None


@dataclass(frozen=True)
class RoleInfo:
    """Rol disponible en el sistema."""

    id: int
    codigo: str
    nombre: str


@dataclass(frozen=True)
class UserSummary:
    """Resumen de usuario para administración."""

    id: int
    username: str
    nombre_completo: str
    rol_id: int
    rol_codigo: str
    rol_nombre: str
    activo: bool
    debe_cambiar_password: bool
    bloqueado_hasta: str | None
    ultimo_login: str | None


@dataclass(frozen=True)
class DashboardSnapshot:
    """Resumen para la pantalla inicial local."""

    empresa_nombre: str
    total_usuarios: int
    total_productos: int
    productos_activos: int
    total_categorias: int
    total_movimientos: int
    total_tipos_movimiento: int
    backup_carpeta: str
    productos_sin_stock: int = 0
    productos_bajo_minimo: int = 0
    entradas_hoy: int = 0
    salidas_hoy: int = 0
    valor_inventario: Decimal = Decimal(0)


class UserRepository(Protocol):
    """Puerto de lectura y escritura de usuarios."""

    def count_users(self) -> int:
        """Devuelve el total de usuarios."""

    def count_active_users(self) -> int:
        """Devuelve el total de usuarios activos."""

    def get_by_id(self, user_id: int) -> AuthUser | None:
        """Busca un usuario por identificador."""

    def get_by_username(self, username: str) -> AuthUser | None:
        """Busca un usuario por nombre de acceso."""

    def add(self, user: AuthUser) -> AuthUser:
        """Crea un usuario nuevo."""

    def save(self, user: AuthUser) -> None:
        """Persiste cambios de un usuario existente."""

    def get_role_by_code(self, code: str) -> RoleInfo | None:
        """Obtiene un rol por su código."""

    def list_roles(self) -> list[RoleInfo]:
        """Lista los roles disponibles."""

    def list_users(self) -> list[UserSummary]:
        """Lista los usuarios registrados."""

    def count_active_admins(self) -> int:
        """Devuelve el total de administradores activos."""

    def list_permission_codes(self, role_id: int) -> set[str]:
        """Lista permisos asignados a un rol."""


class ConfigurationRepository(Protocol):
    """Puerto para configuración persistente."""

    def get_many(self, keys: Sequence[str]) -> dict[str, str]:
        """Obtiene varias claves de configuración."""

    def set_many(self, values: Mapping[str, str]) -> None:
        """Actualiza varias claves de configuración."""


class DashboardRepository(Protocol):
    """Puerto para métricas de la pantalla inicial."""

    def get_snapshot(self) -> DashboardSnapshot:
        """Construye el resumen inicial mostrado en la UI."""
