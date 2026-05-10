from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.application.dtos.peca_dto import PecaEstoqueIn, PecaIn, PecaOut
from app.application.use_cases import peca as u_peca
from app.infrastructure.database import get_session
from app.presentation.dependencies import require_admin
from app.presentation.httpxx import errmap

router = APIRouter(prefix="/pecas", tags=["peças"])


@router.post("", response_model=PecaOut, status_code=201, dependencies=[Depends(require_admin)])
def c(body: PecaIn, db: Session = Depends(get_session)) -> PecaOut:
    try:
        r = u_peca.criar(db, body)
        db.commit()
        return r
    except Exception as e:
        db.rollback()
        c, m = errmap(e)
        raise HTTPException(c, m) from e


@router.get("", response_model=list[PecaOut], dependencies=[Depends(require_admin)])
def ls(db: Session = Depends(get_session)) -> list[PecaOut]:
    return u_peca.listar(db)


@router.get("/{id}", response_model=PecaOut, dependencies=[Depends(require_admin)])
def g(id: int, db: Session = Depends(get_session)) -> PecaOut:
    try:
        return u_peca.obter(db, id)
    except Exception as e:
        c, m = errmap(e)
        raise HTTPException(c, m) from e


@router.put("/{id}", response_model=PecaOut, dependencies=[Depends(require_admin)])
def p(id: int, body: PecaIn, db: Session = Depends(get_session)) -> PecaOut:
    try:
        r = u_peca.atualizar(db, id, body)
        db.commit()
        return r
    except Exception as e:
        db.rollback()
        c, m = errmap(e)
        raise HTTPException(c, m) from e


@router.patch(
    "/{id}/estoque", response_model=PecaOut, dependencies=[Depends(require_admin)]
)
def patch_estoque(
    id: int, body: PecaEstoqueIn, db: Session = Depends(get_session)
) -> PecaOut:
    try:
        r = u_peca.atualizar_estoque(db, id, body)
        db.commit()
        return r
    except Exception as e:
        db.rollback()
        c, m = errmap(e)
        raise HTTPException(c, m) from e


@router.delete("/{id}", status_code=204, response_class=Response, dependencies=[Depends(require_admin)])
def d(id: int, db: Session = Depends(get_session)) -> None:
    try:
        u_peca.deletar(db, id)
        db.commit()
    except Exception as e:
        db.rollback()
        c, m = errmap(e)
        raise HTTPException(c, m) from e
