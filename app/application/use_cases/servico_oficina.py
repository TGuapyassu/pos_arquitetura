from __future__ import annotations

from decimal import Decimal

from app.application.dtos import ServicoIn, ServicoOut
from app.application.mapping.dto_mappers import servico_to_out
from app.domain.entities import ServicoOficina
from app.domain.exceptions import NotFoundError
from app.domain.repositories import IServicoOficinaRepository


class ServicoOficinaService:
    def __init__(self, servicos: IServicoOficinaRepository) -> None:
        self._servicos = servicos

    def criar(self, body: ServicoIn) -> ServicoOut:
        so = ServicoOficina(
            nome=body.nome,
            preco=Decimal(body.preco).quantize(Decimal("0.01")),
        )
        self._servicos.add(so)
        return servico_to_out(so)

    def listar(self) -> list[ServicoOut]:
        return [servico_to_out(x) for x in self._servicos.listar()]

    def obter(self, id: int) -> ServicoOut:
        o = self._servicos.get_by_id(id)
        if o is None:
            raise NotFoundError("Serviço não encontrado.")
        return servico_to_out(o)

    def atualizar(self, id: int, body: ServicoIn) -> ServicoOut:
        o = self._servicos.get_by_id(id)
        if o is None:
            raise NotFoundError("Serviço não encontrado.")
        o.nome = body.nome
        o.preco = Decimal(body.preco).quantize(Decimal("0.01"))
        self._servicos.update(o)
        return servico_to_out(o)

    def deletar(self, id: int) -> None:
        self._servicos.delete(id)
