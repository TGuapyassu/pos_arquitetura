from __future__ import annotations

from typing import Protocol


class IAuthGateway(Protocol):
    def verify_password(self, plain: str, hashed: str) -> bool: ...

    def create_token(self, user_id: int, email: str, is_admin: bool) -> str: ...
