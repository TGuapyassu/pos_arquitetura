from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.application.dtos.ordem_dto import OrdemCreateIn, OrdemOut, OrdemUpdateStatusIn
from app.application.use_cases import ordem_servico as uo
from app.infrastructure.database import get_session
from app.presentation.httpxx import errmap
from app.presentation.dependencies import require_admin

router = APIRouter(prefix="/os", tags=["ordem de serviço"])


@router.post("", response_model=OrdemOut, dependencies=[Depends(require_admin)])
def post_os(
    body: OrdemCreateIn, db: Session = Depends(get_session)
) -> OrdemOut:
    try:
        r = uo.criar_ordem(db, body)
        db.commit()
        return r
    except Exception as e:
        db.rollback()
        c, m = errmap(e)
        raise HTTPException(c, m) from e


@router.get("/{id}", response_model=OrdemOut, dependencies=[Depends(require_admin)])
def get_os(
    id: int, db: Session = Depends(get_session)
) -> OrdemOut:
    try:
        o = uo.obter_os(db, id)
        return o
    except Exception as e:
        c, m = errmap(e)
        raise HTTPException(c, m) from e


@router.get("", response_model=list[OrdemOut], dependencies=[Depends(require_admin)])
def get_list(db: Session = Depends(get_session)) -> list[OrdemOut]:
    return uo.listar_os(db)


@router.patch("/{id}/status", response_model=OrdemOut, dependencies=[Depends(require_admin)])
def patch_status(
    id: int, body: OrdemUpdateStatusIn, db: Session = Depends(get_session)
) -> OrdemOut:
    try:
        r = uo.patch_status(db, id, body)
        db.commit()
        return r
    except Exception as e:
        db.rollback()
        c, m = errmap(e)
        raise HTTPException(c, m) from e


@router.post("/{id}/aprovar", response_model=OrdemOut, dependencies=[Depends(require_admin)])
def aprovar(id: int, db: Session = Depends(get_session)) -> OrdemOut:
    try:
        r = uo.aprovar(db, id)
        db.commit()
        return r
    except Exception as e:
        db.rollback()
        c, m = errmap(e)
        raise HTTPException(c, m) from e
