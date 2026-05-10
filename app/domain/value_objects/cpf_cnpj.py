from __future__ import annotations

import re
from dataclasses import dataclass

from app.domain.exceptions import DomainError


def _apenas_digitos(s: str) -> str:
    return re.sub(r"\D", "", s)


@dataclass(frozen=True, slots=True)
class CpfCnpj:
    """
    CPF (11) ou CNPJ (14) — apenas validação básica de tamanho e checksum simples
    (CPF mod 11). CNPJ: comprimento; checksum completo pode ser acrescentado.
    """

    raw: str

    def __post_init__(self) -> None:
        d = _apenas_digitos(self.raw)
        if not (len(d) == 11 or len(d) == 14):
            raise DomainError("CPF deve ter 11 ou CNPJ 14 dígitos.")
        if len(d) == 11 and not _valida_cpf(d):
            raise DomainError("CPF inválido.")
        if len(d) == 14 and not _valida_cnpj_basico(d):
            raise DomainError("CNPJ inválido (dígitos verificadores).")
        object.__setattr__(self, "raw", d)

    @property
    def value(self) -> str:
        return self.raw

    def __str__(self) -> str:
        return self.raw

    @classmethod
    def parse(cls, value: str) -> CpfCnpj:
        return cls(value)


def _valida_cpf(cpf: str) -> bool:
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False
    s = [int(c) for c in cpf]

    def dv(nums: list[int], pesos: list[int]) -> int:
        w = sum(n * p for n, p in zip(nums, pesos, strict=True)) % 11
        return 0 if w < 2 else 11 - w

    d1 = dv(s[:9], list(range(10, 1, -1)))
    d2 = dv(s[:9] + [d1], list(range(11, 1, -1)))
    return s[9] == d1 and s[10] == d2


def _valida_cnpj_basico(c: str) -> bool:
    if len(c) != 14 or len(set(c)) == 1:
        return False
    s = [int(x) for x in c]
    w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    w2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    d1 = sum(n * w for n, w in zip(s[:12], w1, strict=True)) % 11
    d1 = 0 if d1 < 2 else 11 - d1
    d2 = sum(n * w for n, w in zip(s[:12] + [d1], w2, strict=True)) % 11
    d2 = 0 if d2 < 2 else 11 - d2
    return s[12] == d1 and s[13] == d2
