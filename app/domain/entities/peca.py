from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from app.domain.exceptions import DomainError


@dataclass
class Peca:
    nome: str
    preco: Decimal
    quantidade_estoque: int
    id: Optional[int] = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def reservar_ou_baixar(self, qtd: int) -> None:
        """Estoque nunca fica negativo; chamado pelo caso de uso ao vincular à OS."""
        if qtd <= 0:
            raise DomainError("Quantidade deve ser positiva.")
        if self.quantidade_estoque < qtd:
            from app.domain.exceptions import EstoqueInsuficienteError

            raise EstoqueInsuficienteError(self.id or 0, qtd, self.quantidade_estoque)
        self.quantidade_estoque -= qtd

    def repor(self, qtd: int) -> None:
        if qtd < 0:
            raise DomainError("Quantidade de reposição inválida.")
        self.quantidade_estoque += qtd

    def definir_estoque(self, total: int) -> None:
        if total < 0:
            raise DomainError("Estoque não pode ser negativo.")
        self.quantidade_estoque = total
