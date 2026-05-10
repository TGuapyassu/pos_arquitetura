from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VeiculoIn(BaseModel):
    cliente_id: int
    placa: str = Field(min_length=7, max_length=8)
    marca: str
    modelo: str
    ano: int = Field(ge=1980, le=2035)


class VeiculoOut(BaseModel):
    id: int
    cliente_id: int
    placa: str
    marca: str
    modelo: str
    ano: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
