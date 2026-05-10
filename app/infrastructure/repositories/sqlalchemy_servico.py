from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import ServicoOficina
from app.domain.exceptions import NotFoundError
from app.infrastructure.database.models import ServicoOrm
from app.infrastructure.mappers.entity_mappers import servico_orm_to_domain


class SqlAlchemyServicoOficinaRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def add(self, s: ServicoOficina) -> ServicoOficina:
        m = ServicoOrm(nome=s.nome, preco=s.preco)
        self._s.add(m)
        self._s.flush()
        self._s.refresh(m)
        s.id = m.id
        s.created_at = m.created_at
        s.updated_at = m.updated_at
        return s

    def update(self, s: ServicoOficina) -> ServicoOficina:
        if s.id is None:
            raise ValueError("id obrigatório")
        m = self._s.get(ServicoOrm, s.id)
        if m is None:
            raise NotFoundError("Serviço não encontrado.")
        m.nome = s.nome
        m.preco = s.preco
        m.updated_at = datetime.now(timezone.utc)
        self._s.flush()
        return s

    def get_by_id(self, id: int) -> Optional[ServicoOficina]:
        m = self._s.get(ServicoOrm, id)
        return None if m is None else servico_orm_to_domain(m)

    def listar(self) -> List[ServicoOficina]:
        rows = self._s.execute(select(ServicoOrm).order_by(ServicoOrm.id)).scalars()
        return [servico_orm_to_domain(m) for m in rows]

    def delete(self, id: int) -> None:
        m = self._s.get(ServicoOrm, id)
        if m is None:
            raise NotFoundError("Serviço não encontrado.")
        self._s.delete(m)
        self._s.flush()
