"""Errores funcionales y de dominio."""

from __future__ import annotations


class DomainError(Exception):
    """Base para errores funcionales con código estable."""

    default_code = "ERROR_DOMINIO"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.default_code


class ValidationError(DomainError):
    default_code = "VALIDACION"


class PermissionDenied(DomainError):
    default_code = "SIN_PERMISO"


class NotFoundError(DomainError):
    default_code = "NO_ENCONTRADO"


class ConflictError(DomainError):
    default_code = "CONFLICTO"


class BusinessRuleViolation(DomainError):
    default_code = "REGLA_NEGOCIO"
