from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from pydantic import BaseModel, Field

from app.infrastructure.config import get_settings


class TokenPayload(BaseModel):
    sub: str
    user_id: int
    is_admin: bool
    exp: int


def create_token(user_id: int, email: str, is_admin: bool) -> str:
    s = get_settings()
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=s.access_token_expire_minutes)
    to_encode: dict[str, Any] = {
        "sub": email,
        "user_id": user_id,
        "is_admin": is_admin,
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(to_encode, s.jwt_secret, algorithm=s.jwt_algorithm)


def verify_token(token: str) -> Optional[TokenPayload]:
    s = get_settings()
    try:
        p = jwt.decode(token, s.jwt_secret, algorithms=[s.jwt_algorithm])
        return TokenPayload(
            sub=p["sub"],
            user_id=int(p["user_id"]),
            is_admin=bool(p.get("is_admin", False)),
            exp=int(p["exp"]),
        )
    except (JWTError, KeyError, TypeError, ValueError):
        return None
