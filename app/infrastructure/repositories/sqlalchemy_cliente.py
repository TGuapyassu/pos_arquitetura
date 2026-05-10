from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import Cliente
from app.infrastructure.database.models import ClienteOrm
from app.infrastructure.mappers.entity_mappers import cliente_orm_to_domain
from app.domain.exceptions import NotFoundError


class SqlAlchemyClienteRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def add(self, c: Cliente) -> Cliente:
        m = ClienteOrm(
            cpf_cnpj=c.cpf_cnpj,
            nome=c.nome,
            contato=c.contato,
        )
        self._s.add(m)
        self._s.flush()
        self._s.refresh(m)
        c.id = m.id
        c.created_at = m.created_at
        c.updated_at = m.updated_at
        return c

    def update(self, c: Cliente) -> Cliente:
        if c.id is None:
            raise ValueError("id obrigatório")
        m = self._s.get(ClienteOrm, c.id)
        if m is None:
            raise NotFoundError("Cliente não encontrado.")
        m.nome = c.nome
        m.contato = c.contato
        m.cpf_cnpj = c.cpf_cnpj
        m.updated_at = datetime.now(timezone.utc)
        self._s.flush()
        return c

    def get_by_id(self, id: int) -> Optional[Cliente]:
        m = self._s.get(ClienteOrm, id)
        return None if m is None else cliente_orm_to_domain(m)

    def listar(self) -> List[Cliente]:
        rows = self._s.execute(select(ClienteOrm).order_by(ClienteOrm.id)).scalars()
        return [cliente_orm_to_domain(m) for m in rows]

    def delete(self, id: int) -> None:
        m = self._s.get(ClienteOrm, id)
        if m is None:
            raise NotFoundError("Cliente não encontrado.")
        self._s.delete(m)
        self._s.flush()
