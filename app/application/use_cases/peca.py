from __future__ import annotations

from decimal import Decimal

from app.application.dtos.peca_dto import PecaEstoqueIn, PecaIn, PecaOut
from app.application.mapping.dto_mappers import peca_to_out
from app.domain.entities import Peca
from app.domain.exceptions import NotFoundError
from app.domain.repositories import IPecaRepository


class PecaService:
    def __init__(self, pecas: IPecaRepository) -> None:
        self._pecas = pecas

    def criar(self, body: PecaIn) -> PecaOut:
        p = Peca(
            nome=body.nome,
            preco=Decimal(body.preco).quantize(Decimal("0.01")),
            quantidade_estoque=body.quantidade_estoque,
        )
        self._pecas.add(p)
        return peca_to_out(p)

    def listar(self) -> list[PecaOut]:
        return [peca_to_out(x) for x in self._pecas.listar()]

    def obter(self, id: int) -> PecaOut:
        p = self._pecas.get_by_id(id)
        if p is None:
            raise NotFoundError("Peça não encontrada.")
        return peca_to_out(p)

    def atualizar(self, id: int, body: PecaIn) -> PecaOut:
        p = self._pecas.get_by_id(id)
        if p is None:
            raise NotFoundError("Peça não encontrada.")
        p.nome = body.nome
        p.preco = Decimal(body.preco).quantize(Decimal("0.01"))
        p.definir_estoque(body.quantidade_estoque)
        self._pecas.update(p)
        return peca_to_out(p)

    def atualizar_estoque(self, id: int, body: PecaEstoqueIn) -> PecaOut:
        p = self._pecas.get_by_id(id)
        if p is None:
            raise NotFoundError("Peça não encontrada.")
        if body.ajuste_absoluto:
            p.definir_estoque(body.quantidade)
        else:
            p.definir_estoque(p.quantidade_estoque + body.quantidade)
        self._pecas.update(p)
        return peca_to_out(p)

    def deletar(self, id: int) -> None:
        self._pecas.delete(id)
