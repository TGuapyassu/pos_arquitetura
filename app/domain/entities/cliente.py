from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Cliente:
    """
    Agregado Cliente. CPF/CNPJ (somente dígitos validados na aplicação)
    e contato (telefone ou e-mail exibido no cadastro).
    """

    nome: str
    contato: str
    cpf_cnpj: str
    id: Optional[int] = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
