from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ServicoIn(BaseModel):
    nome: str = Field(min_length=1, max_length=200)
    preco: Decimal = Field(ge=0)

    @field_validator("preco", mode="before")
    @classmethod
    def d(cls, v: object) -> object:
        if v is not None and isinstance(v, (int, float, str)):
            return Decimal(str(v))
        return v


class ServicoOut(BaseModel):
    id: int
    nome: str
    preco: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
