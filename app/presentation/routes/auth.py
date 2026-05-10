from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.application.dtos import LoginIn, TokenOut
from app.application.use_cases import auth as uauth
from app.infrastructure.database import get_session
from app.presentation.httpxx import errmap

router = APIRouter(prefix="/auth", tags=["autenticacao"])


@router.post("/login", response_model=TokenOut)
def login(
    body: LoginIn, db: Session = Depends(get_session)
) -> TokenOut:
    try:
        t = uauth.login(db, body)
        db.commit()
        return t
    except Exception as e:  # noqa: BLE001
        db.rollback()
        c, m = errmap(e)
        raise HTTPException(c, m) from e
