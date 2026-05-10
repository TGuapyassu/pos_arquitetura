from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Usuario:
    email: str
    senha_hash: str
    is_admin: bool
    is_active: bool = True
    id: Optional[int] = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
