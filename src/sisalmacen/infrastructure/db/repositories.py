"""Repositorios base sobre SQLAlchemy."""

from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from sisalmacen.domain.repositories import Repository
from sisalmacen.infrastructure.db.base import Base

EntityT = TypeVar("EntityT", bound=Base)
IdT = TypeVar("IdT")


class SqlAlchemyRepository(Repository[EntityT, IdT], Generic[EntityT, IdT]):
    """Implementación mínima de repositorio para la Entrega 0."""

    def __init__(self, session: Session, model_type: type[EntityT]) -> None:
        self.session = session
        self.model_type = model_type

    def add(self, entity: EntityT) -> None:
        self.session.add(entity)

    def get_by_id(self, entity_id: IdT) -> EntityT | None:
        return self.session.get(self.model_type, entity_id)
