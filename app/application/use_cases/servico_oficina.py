from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.application.dtos import ServicoIn, ServicoOut
from app.application.mapping.dto_mappers import servico_to_out
from app.domain.entities import ServicoOficina
from app.domain.exceptions import NotFoundError
from app.infrastructure.repositories.sqlalchemy_servico import SqlAlchemyServicoOficinaRepository


def _r(s: Session) -> SqlAlchemyServicoOficinaRepository:
    return SqlAlchemyServicoOficinaRepository(s)


def criar(s: Session, body: ServicoIn) -> ServicoOut:
    so = ServicoOficina(
        nome=body.nome,
        preco=Decimal(body.preco).quantize(Decimal("0.01")),
    )
    _r(s).add(so)
    return servico_to_out(so)


def listar(s: Session) -> list[ServicoOut]:
    return [servico_to_out(x) for x in _r(s).listar()]


def obter(s: Session, id: int) -> ServicoOut:
    o = _r(s).get_by_id(id)
    if o is None:
        raise NotFoundError("Serviço não encontrado.")
    return servico_to_out(o)


def atualizar(s: Session, id: int, body: ServicoIn) -> ServicoOut:
    repo = _r(s)
    o = repo.get_by_id(id)
    if o is None:
        raise NotFoundError("Serviço não encontrado.")
    o.nome = body.nome
    o.preco = Decimal(body.preco).quantize(Decimal("0.01"))
    repo.update(o)
    return servico_to_out(o)


def deletar(s: Session, id: int) -> None:
    _r(s).delete(id)
