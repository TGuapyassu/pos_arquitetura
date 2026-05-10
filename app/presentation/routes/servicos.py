from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.application.dtos import ServicoIn, ServicoOut
from app.application.use_cases import servico_oficina as u_serv
from app.infrastructure.database import get_session
from app.presentation.dependencies import require_admin
from app.presentation.httpxx import errmap

router = APIRouter(prefix="/servicos", tags=["serviços"])


@router.post("", response_model=ServicoOut, status_code=201, dependencies=[Depends(require_admin)])
def c(body: ServicoIn, db: Session = Depends(get_session)) -> ServicoOut:
    try:
        r = u_serv.criar(db, body)
        db.commit()
        return r
    except Exception as e:
        db.rollback()
        c, m = errmap(e)
        raise HTTPException(c, m) from e


@router.get("", response_model=list[ServicoOut], dependencies=[Depends(require_admin)])
def ls(db: Session = Depends(get_session)) -> list[ServicoOut]:
    return u_serv.listar(db)


@router.get("/{id}", response_model=ServicoOut, dependencies=[Depends(require_admin)])
def g(id: int, db: Session = Depends(get_session)) -> ServicoOut:
    try:
        return u_serv.obter(db, id)
    except Exception as e:
        c, m = errmap(e)
        raise HTTPException(c, m) from e


@router.put("/{id}", response_model=ServicoOut, dependencies=[Depends(require_admin)])
def p(id: int, body: ServicoIn, db: Session = Depends(get_session)) -> ServicoOut:
    try:
        r = u_serv.atualizar(db, id, body)
        db.commit()
        return r
    except Exception as e:
        db.rollback()
        c, m = errmap(e)
        raise HTTPException(c, m) from e


@router.delete("/{id}", status_code=204, response_class=Response, dependencies=[Depends(require_admin)])
def d(id: int, db: Session = Depends(get_session)) -> None:
    try:
        u_serv.deletar(db, id)
        db.commit()
    except Exception as e:
        db.rollback()
        c, m = errmap(e)
        raise HTTPException(c, m) from e
