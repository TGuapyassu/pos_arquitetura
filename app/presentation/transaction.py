from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.presentation.httpxx import errmap

T = TypeVar("T")


def run_in_transaction(db: Session, fn: Callable[[], T]) -> T:
    try:
        result = fn()
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        code, msg = errmap(e)
        raise HTTPException(code, msg) from e


def handle_domain_errors(fn: Callable[[], T]) -> T:
    try:
        return fn()
    except Exception as e:
        code, msg = errmap(e)
        raise HTTPException(code, msg) from e
