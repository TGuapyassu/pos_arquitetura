from __future__ import annotations

from sqlalchemy.orm import Session

from app.application.dtos import VeiculoIn, VeiculoOut
from app.application.mapping.dto_mappers import veiculo_to_out
from app.domain.entities import Veiculo
from app.domain.exceptions import NotFoundError
from app.domain.value_objects import Placa
from app.infrastructure.repositories.sqlalchemy_cliente import SqlAlchemyClienteRepository
from app.infrastructure.repositories.sqlalchemy_veiculo import SqlAlchemyVeiculoRepository


def _v(s: Session) -> SqlAlchemyVeiculoRepository:
    return SqlAlchemyVeiculoRepository(s)


def _c(s: Session) -> SqlAlchemyClienteRepository:
    return SqlAlchemyClienteRepository(s)


def criar(s: Session, body: VeiculoIn) -> VeiculoOut:
    if _c(s).get_by_id(body.cliente_id) is None:
        raise NotFoundError("Cliente não encontrado.")
    pl = Placa.parse(body.placa)
    v = Veiculo(
        cliente_id=body.cliente_id,
        placa=pl.value,
        marca=body.marca,
        modelo=body.modelo,
        ano=body.ano,
    )
    _v(s).add(v)
    return veiculo_to_out(v)


def listar(s: Session) -> list[VeiculoOut]:
    return [veiculo_to_out(x) for x in _v(s).listar()]


def listar_por_cliente(s: Session, cliente_id: int) -> list[VeiculoOut]:
    if _c(s).get_by_id(cliente_id) is None:
        raise NotFoundError("Cliente não encontrado.")
    return [veiculo_to_out(x) for x in _v(s).listar_por_cliente(cliente_id)]


def obter(s: Session, id: int) -> VeiculoOut:
    v = _v(s).get_by_id(id)
    if v is None:
        raise NotFoundError("Veículo não encontrado.")
    return veiculo_to_out(v)


def atualizar(s: Session, id: int, body: VeiculoIn) -> VeiculoOut:
    r = _v(s)
    v = r.get_by_id(id)
    if v is None:
        raise NotFoundError("Veículo não encontrado.")
    if _c(s).get_by_id(body.cliente_id) is None:
        raise NotFoundError("Cliente não encontrado.")
    pl = Placa.parse(body.placa)
    v.placa = pl.value
    v.marca = body.marca
    v.modelo = body.modelo
    v.ano = body.ano
    v.cliente_id = body.cliente_id
    r.update(v)
    return veiculo_to_out(v)


def deletar(s: Session, id: int) -> None:
    _v(s).delete(id)
