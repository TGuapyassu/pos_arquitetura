from __future__ import annotations

import re
from dataclasses import dataclass

from app.domain.exceptions import DomainError


# Mercosul: 7 caracteres (LLLNLDN) | Antiga: 7 (LLLNNNN)
_PATR = re.compile(
    r"^([A-Z]{3}\d{4}|[A-Z]{3}\d[A-Z0-9]\d{2})$", re.IGNORECASE
)


@dataclass(frozen=True, slots=True)
class Placa:
    raw: str

    def __post_init__(self) -> None:
        t = self.raw.replace(" ", "").replace("-", "").upper()
        s = t
        if not _PATR.match(s):
            raise DomainError("Placa inválida (formato Mercosul ou antigo).")
        object.__setattr__(self, "raw", s)

    @classmethod
    def parse(cls, value: str) -> "Placa":
        return cls(value)

    @property
    def value(self) -> str:
        return self.raw

    def __str__(self) -> str:
        return self.raw
