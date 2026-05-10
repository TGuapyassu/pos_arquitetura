from __future__ import annotations

from passlib.context import CryptContext

_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=10)


def hash_password(s: str) -> str:
    return _ctx.hash(s)


def verify_password(plain: str, hashed: str) -> bool:
    return _ctx.verify(plain, hashed)
