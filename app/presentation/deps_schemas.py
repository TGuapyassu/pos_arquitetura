from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TokenData:
    sub: str
    user_id: int
    is_admin: bool
