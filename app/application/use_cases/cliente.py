from __future__ import annotations

from sqlalchemy.orm import Session

from app.application.dtos import ClienteIn, ClienteOut
from app.application.mapping.dto_mappers import cliente_to_out
from app.domain.entities import Cliente
from app.domain.exceptions import NotFoundError
from app.domain.value_objects import CpfCnpj
from app.infrastructure.repositories.sqlalchemy_cliente import SqlAlchemyClienteRepository


def _repo(s: Session) -> SqlAlchemyClienteRepository:
    return SqlAlchemyClienteRepository(s)


def criar(s: Session, body: ClienteIn) -> ClienteOut:
    doc = CpfCnpj.parse(body.cpf_cnpj)
    c = Cliente(
        nome=body.nome,
        contato=body.contato,
        cpf_cnpj=doc.value,
    )
    _repo(s).add(c)
    return cliente_to_out(c)


def listar(s: Session) -> list[ClienteOut]:
    return [cliente_to_out(c) for c in _repo(s).listar()]


def obter(s: Session, id: int) -> ClienteOut:
    c = _repo(s).get_by_id(id)
    if c is None:
        raise NotFoundError("Cliente não encontrado.")
    return cliente_to_out(c)


def atualizar(s: Session, id: int, body: ClienteIn) -> ClienteOut:
    r = _repo(s)
    c = r.get_by_id(id)
    if c is None:
        raise NotFoundError("Cliente não encontrado.")
    doc = CpfCnpj.parse(body.cpf_cnpj)
    c.nome = body.nome
    c.contato = body.contato
    c.cpf_cnpj = doc.value
    r.update(c)
    return cliente_to_out(c)


def deletar(s: Session, id: int) -> None:
    _repo(s).delete(id)
