from __future__ import annotations

from app.application.dtos import ClienteIn, ClienteOut
from app.application.mapping.dto_mappers import cliente_to_out
from app.domain.entities import Cliente
from app.domain.exceptions import NotFoundError
from app.domain.repositories import IClienteRepository
from app.domain.value_objects import CpfCnpj


class ClienteService:
    def __init__(self, clientes: IClienteRepository) -> None:
        self._clientes = clientes

    def criar(self, body: ClienteIn) -> ClienteOut:
        doc = CpfCnpj.parse(body.cpf_cnpj)
        c = Cliente(
            nome=body.nome,
            contato=body.contato,
            cpf_cnpj=doc.value,
        )
        self._clientes.add(c)
        return cliente_to_out(c)

    def listar(self) -> list[ClienteOut]:
        return [cliente_to_out(c) for c in self._clientes.listar()]

    def obter(self, id: int) -> ClienteOut:
        c = self._clientes.get_by_id(id)
        if c is None:
            raise NotFoundError("Cliente não encontrado.")
        return cliente_to_out(c)

    def atualizar(self, id: int, body: ClienteIn) -> ClienteOut:
        c = self._clientes.get_by_id(id)
        if c is None:
            raise NotFoundError("Cliente não encontrado.")
        doc = CpfCnpj.parse(body.cpf_cnpj)
        c.nome = body.nome
        c.contato = body.contato
        c.cpf_cnpj = doc.value
        self._clientes.update(c)
        return cliente_to_out(c)

    def deletar(self, id: int) -> None:
        self._clientes.delete(id)
