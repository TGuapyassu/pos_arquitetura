from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.application.dtos import LoginIn, TokenOut
from app.application.use_cases.auth import LoginUseCase
from app.infrastructure.database import get_session
from app.presentation.composition import get_login_use_case
from app.presentation.transaction import run_in_transaction

router = APIRouter(prefix="/auth", tags=["autenticacao"])


@router.post("/login", response_model=TokenOut)
def login(
    body: LoginIn,
    db: Session = Depends(get_session),
    use_case: LoginUseCase = Depends(get_login_use_case),
) -> TokenOut:
    return run_in_transaction(db, lambda: use_case.execute(body))
