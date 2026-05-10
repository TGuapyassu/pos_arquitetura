from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import Veiculo
from app.domain.exceptions import NotFoundError
from app.infrastructure.database.models import VeiculoOrm
from app.infrastructure.mappers.entity_mappers import veiculo_orm_to_domain


class SqlAlchemyVeiculoRepository:
    def __init__(self, session: Session) -> None:
        self._s = session

    def add(self, v: Veiculo) -> Veiculo:
        m = VeiculoOrm(
            cliente_id=v.cliente_id,
            placa=v.placa,
            marca=v.marca,
            modelo=v.modelo,
            ano=v.ano,
        )
        self._s.add(m)
        self._s.flush()
        self._s.refresh(m)
        v.id = m.id
        v.created_at = m.created_at
        v.updated_at = m.updated_at
        return v

    def update(self, v: Veiculo) -> Veiculo:
        if v.id is None:
            raise ValueError("id obrigatório")
        m = self._s.get(VeiculoOrm, v.id)
        if m is None:
            raise NotFoundError("Veículo não encontrado.")
        m.placa = v.placa
        m.marca = v.marca
        m.modelo = v.modelo
        m.ano = v.ano
        m.cliente_id = v.cliente_id
        m.updated_at = datetime.now(timezone.utc)
        self._s.flush()
        return v

    def get_by_id(self, id: int) -> Optional[Veiculo]:
        m = self._s.get(VeiculoOrm, id)
        return None if m is None else veiculo_orm_to_domain(m)

    def listar_por_cliente(self, cliente_id: int) -> List[Veiculo]:
        q = (
            self._s.execute(
                select(VeiculoOrm)
                .where(VeiculoOrm.cliente_id == cliente_id)
                .order_by(VeiculoOrm.id)
            )
        ).scalars()
        return [veiculo_orm_to_domain(m) for m in q]

    def listar(self) -> List[Veiculo]:
        q = self._s.execute(select(VeiculoOrm).order_by(VeiculoOrm.id)).scalars()
        return [veiculo_orm_to_domain(m) for m in q]

    def delete(self, id: int) -> None:
        m = self._s.get(VeiculoOrm, id)
        if m is None:
            raise NotFoundError("Veículo não encontrado.")
        self._s.delete(m)
        self._s.flush()
