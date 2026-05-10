from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Veiculo:
    """Veículo pertencente a um Cliente (integridade relacional no ORM + FK)."""

    cliente_id: int
    placa: str
    marca: str
    modelo: str
    ano: int
    id: Optional[int] = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
