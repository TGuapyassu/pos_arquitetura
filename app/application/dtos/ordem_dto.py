from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.domain.enums import OrdemServicoStatus


class OrdemItemServicoIn(BaseModel):
    servico_id: int
    quantidade: int = Field(ge=1)


class OrdemItemPecaIn(BaseModel):
    peca_id: int
    quantidade: int = Field(ge=1)


class OrdemCreateIn(BaseModel):
    cliente_id: int
    veiculo_id: int
    servicos: List[OrdemItemServicoIn] = Field(default_factory=list)
    pecas: List[OrdemItemPecaIn] = Field(default_factory=list)


class OrdemItemOut(BaseModel):
    servico_id: Optional[int] = None
    peca_id: Optional[int] = None
    quantidade: int
    preco_unitario: Decimal


class OrdemOut(BaseModel):
    id: int
    cliente_id: int
    veiculo_id: int
    status: OrdemServicoStatus
    valor_total: Decimal
    aprovada_em: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    data_finalizacao: Optional[datetime] = None
    data_entrega: Optional[datetime] = None
    servicos: List[OrdemItemOut]
    pecas: List[OrdemItemOut]


class OrdemUpdateStatusIn(BaseModel):
    status: OrdemServicoStatus


class OrdemPublicaOut(BaseModel):
    """Resposta pública: status e totais, sem detalhes administrativos extras."""

    id: int
    status: OrdemServicoStatus
    valor_total: Decimal
    data_finalizacao: Optional[datetime] = None
    data_entrega: Optional[datetime] = None
