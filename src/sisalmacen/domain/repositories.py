"""Protocolos base de repositorios del dominio."""

from __future__ import annotations

from typing import Protocol, TypeVar

EntityT = TypeVar("EntityT")
IdT = TypeVar("IdT", contravariant=True)


class Repository(Protocol[EntityT, IdT]):
    """Contrato mínimo para repositorios inyectables."""

    def add(self, entity: EntityT) -> None:
        """Agrega una entidad a la unidad de trabajo."""

    def get_by_id(self, entity_id: IdT) -> EntityT | None:
        """Obtiene una entidad por su identificador."""
