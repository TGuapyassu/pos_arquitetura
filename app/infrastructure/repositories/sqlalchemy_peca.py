from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import Peca
from app.domain.exceptions import NotFoundError
from app.infrastructure.database.models import PecaOrm
from app.infrastructure.mappers.entity_mappers import peca_orm_to_domain


class SqlAlchemyPecaRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def add(self, p: Peca) -> Peca:
        m = PecaOrm(
            nome=p.nome,
            preco=p.preco,
            quantidade_estoque=p.quantidade_estoque,
        )
        self._s.add(m)
        self._s.flush()
        self._s.refresh(m)
        p.id = m.id
        p.created_at = m.created_at
        p.updated_at = m.updated_at
        return p

    def update(self, p: Peca) -> Peca:
        if p.id is None:
            raise ValueError("id obrigatório")
        m = self._s.get(PecaOrm, p.id)
        if m is None:
            raise NotFoundError("Peça não encontrada.")
        m.nome = p.nome
        m.preco = p.preco
        m.quantidade_estoque = p.quantidade_estoque
        m.updated_at = datetime.now(timezone.utc)
        self._s.flush()
        return p

    def get_by_id(self, id: int) -> Optional[Peca]:
        m = self._s.get(PecaOrm, id)
        return None if m is None else peca_orm_to_domain(m)

    def listar(self) -> List[Peca]:
        q = self._s.execute(select(PecaOrm).order_by(PecaOrm.id)).scalars()
        return [peca_orm_to_domain(m) for m in q]

    def listar_por_ids(self, ids: List[int]) -> List[Peca]:
        if not ids:
            return []
        q = self._s.execute(
            select(PecaOrm).where(PecaOrm.id.in_(set(ids)))
        ).scalars()
        return [peca_orm_to_domain(m) for m in q]

    def delete(self, id: int) -> None:
        m = self._s.get(PecaOrm, id)
        if m is None:
            raise NotFoundError("Peça não encontrada.")
        self._s.delete(m)
        self._s.flush()
