from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.domain.entities import OrdemServico
from app.domain.enums import OrdemServicoStatus
from app.infrastructure.database.models import OrdemServicoOrm
from app.infrastructure.mappers.entity_mappers import os_orm_to_domain, sync_os_domain_to_orm
from app.domain.exceptions import NotFoundError


class SqlAlchemyOrdemServicoRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def _load(self, id: int) -> OrdemServico:
        o = self._s.execute(
            select(OrdemServicoOrm)
            .where(OrdemServicoOrm.id == id)
            .options(
                selectinload(OrdemServicoOrm.itens_servico),
                selectinload(OrdemServicoOrm.itens_peca),
            )
        ).scalars().one_or_none()
        if o is None:
            raise NotFoundError("Ordem de serviço não encontrada.")
        return o

    def add(self, o: OrdemServico) -> OrdemServico:
        m = OrdemServicoOrm()
        sync_os_domain_to_orm(o, m)
        o.updated_at = datetime.now(timezone.utc)
        self._s.add(m)
        self._s.flush()
        self._s.refresh(m, ["itens_servico", "itens_peca"])
        o.id = m.id
        o.created_at = m.created_at
        o.updated_at = m.updated_at
        o.valor_total = m.valor_total
        return o

    def update(self, o: OrdemServico) -> OrdemServico:
        if o.id is None:
            raise ValueError("id obrigatório")
        m = self._load(int(o.id))
        sync_os_domain_to_orm(o, m)
        o.updated_at = m.updated_at = datetime.now(timezone.utc)
        self._s.flush()
        return o

    def get_by_id(self, id: int) -> Optional[OrdemServico]:
        o = self._s.execute(
            select(OrdemServicoOrm)
            .where(OrdemServicoOrm.id == id)
            .options(
                selectinload(OrdemServicoOrm.itens_servico),
                selectinload(OrdemServicoOrm.itens_peca),
            )
        ).scalars().one_or_none()
        if o is None:
            return None
        return os_orm_to_domain(o)

    def listar(self) -> List[OrdemServico]:
        q = self._s.execute(
            select(OrdemServicoOrm)
            .order_by(OrdemServicoOrm.id.desc())
            .options(
                selectinload(OrdemServicoOrm.itens_servico),
                selectinload(OrdemServicoOrm.itens_peca),
            )
        ).scalars()
        return [os_orm_to_domain(m) for m in q]

    def listar_ativas(self) -> List[OrdemServico]:
        q = self._s.execute(
            select(OrdemServicoOrm)
            .where(
                OrdemServicoOrm.status.not_in(
                    [OrdemServicoStatus.FINALIZADA, OrdemServicoStatus.ENTREGUE]
                )
            )
            .order_by(OrdemServicoOrm.created_at.asc())
            .options(
                selectinload(OrdemServicoOrm.itens_servico),
                selectinload(OrdemServicoOrm.itens_peca),
            )
        ).scalars()
        return [os_orm_to_domain(m) for m in q]
