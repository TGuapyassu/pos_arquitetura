from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from app.domain.exceptions import DomainError


@dataclass(frozen=True, slots=True)
class Dinheiro:
    """
    Valor monetário (centavos internamente para evitar float).
    O armazenamento no ORM continua em Decimal/NUMERIC; conversão na borda.
    """

    _centavos: int

    @classmethod
    def from_reais(cls, reais: Decimal) -> Dinheiro:
        if reais < 0:
            raise DomainError("Valor não pode ser negativo.")
        cent = int((reais * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        return cls(_centavos=cent)

    @classmethod
    def from_cents_int(cls, centavos: int) -> Dinheiro:
        if centavos < 0:
            raise DomainError("Valor não pode ser negativo.")
        return cls(_centavos=centavos)

    def to_decimal(self) -> Decimal:
        return (Decimal(self._centavos) / Decimal(100)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    def adicionar(self, outro: Dinheiro) -> Dinheiro:
        return Dinheiro.from_cents_int(self._centavos + outro._centavos)

    @property
    def centavos(self) -> int:
        return self._centavos
