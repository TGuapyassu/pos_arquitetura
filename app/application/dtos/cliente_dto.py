from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ClienteIn(BaseModel):
    nome: str = Field(min_length=2, max_length=255)
    contato: str = Field(min_length=3, max_length=120)
    cpf_cnpj: str = Field(min_length=11, max_length=18, description="CPF ou CNPJ (com ou sem máscara)")


class ClienteOut(BaseModel):
    id: int
    nome: str
    contato: str
    cpf_cnpj: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
