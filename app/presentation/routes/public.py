from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.application.dtos.ordem_dto import OrdemPublicaOut
from app.application.use_cases import ordem_servico as uo
from app.infrastructure.database import get_session
from app.presentation.httpxx import errmap

router = APIRouter(prefix="/public", tags=["público"])


@router.get(
    "/ordens-servico/{id}",
    response_model=OrdemPublicaOut,
    summary="Consulta pública de OS (cliente) — sem autenticação",
)
def get_public(
    id: int, db: Session = Depends(get_session)
) -> OrdemPublicaOut:
    try:
        return uo.public_obter_os(db, id)
    except Exception as e:
        c, m = errmap(e)
        raise HTTPException(c, m) from e
