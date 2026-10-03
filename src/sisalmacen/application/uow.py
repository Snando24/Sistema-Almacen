"""Contrato de unidad de trabajo para casos de uso."""

from __future__ import annotations

from abc import ABC, abstractmethod


class UnitOfWork(ABC):
    """Unidad de trabajo abstracta para coordinar transacciones."""

    def __enter__(self) -> UnitOfWork:
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        if exc_type is None:
            return
        self.rollback()

    @abstractmethod
    def commit(self) -> None:
        """Confirma la transacción activa."""

    @abstractmethod
    def rollback(self) -> None:
        """Revierte la transacción activa."""
