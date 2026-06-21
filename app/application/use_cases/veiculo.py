from __future__ import annotations

from app.application.dtos import VeiculoIn, VeiculoOut
from app.application.mapping.dto_mappers import veiculo_to_out
from app.domain.entities import Veiculo
from app.domain.exceptions import NotFoundError
from app.domain.repositories import IClienteRepository, IVeiculoRepository
from app.domain.value_objects import Placa


class VeiculoService:
    def __init__(
        self,
        veiculos: IVeiculoRepository,
        clientes: IClienteRepository,
    ) -> None:
        self._veiculos = veiculos
        self._clientes = clientes

    def criar(self, body: VeiculoIn) -> VeiculoOut:
        if self._clientes.get_by_id(body.cliente_id) is None:
            raise NotFoundError("Cliente não encontrado.")
        pl = Placa.parse(body.placa)
        v = Veiculo(
            cliente_id=body.cliente_id,
            placa=pl.value,
            marca=body.marca,
            modelo=body.modelo,
            ano=body.ano,
        )
        self._veiculos.add(v)
        return veiculo_to_out(v)

    def listar(self) -> list[VeiculoOut]:
        return [veiculo_to_out(x) for x in self._veiculos.listar()]

    def listar_por_cliente(self, cliente_id: int) -> list[VeiculoOut]:
        if self._clientes.get_by_id(cliente_id) is None:
            raise NotFoundError("Cliente não encontrado.")
        return [veiculo_to_out(x) for x in self._veiculos.listar_por_cliente(cliente_id)]

    def obter(self, id: int) -> VeiculoOut:
        v = self._veiculos.get_by_id(id)
        if v is None:
            raise NotFoundError("Veículo não encontrado.")
        return veiculo_to_out(v)

    def atualizar(self, id: int, body: VeiculoIn) -> VeiculoOut:
        v = self._veiculos.get_by_id(id)
        if v is None:
            raise NotFoundError("Veículo não encontrado.")
        if self._clientes.get_by_id(body.cliente_id) is None:
            raise NotFoundError("Cliente não encontrado.")
        pl = Placa.parse(body.placa)
        v.placa = pl.value
        v.marca = body.marca
        v.modelo = body.modelo
        v.ano = body.ano
        v.cliente_id = body.cliente_id
        self._veiculos.update(v)
        return veiculo_to_out(v)

    def deletar(self, id: int) -> None:
        self._veiculos.delete(id)
