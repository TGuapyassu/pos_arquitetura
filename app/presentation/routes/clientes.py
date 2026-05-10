from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.application.dtos import ClienteIn, ClienteOut
from app.application.use_cases import cliente as ucli
from app.infrastructure.database import get_session
from app.presentation.dependencies import require_admin
from app.presentation.httpxx import errmap

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.post("", response_model=ClienteOut, status_code=201, dependencies=[Depends(require_admin)])
def c(body: ClienteIn, db: Session = Depends(get_session)) -> ClienteOut:
    try:
        r = ucli.criar(db, body)
        db.commit()
        return r
    except Exception as e:
        db.rollback()
        c, m = errmap(e)
        raise HTTPException(c, m) from e


@router.get("", response_model=list[ClienteOut], dependencies=[Depends(require_admin)])
def ls(db: Session = Depends(get_session)) -> list[ClienteOut]:
    return ucli.listar(db)


@router.get("/{id}", response_model=ClienteOut, dependencies=[Depends(require_admin)])
def g(id: int, db: Session = Depends(get_session)) -> ClienteOut:
    try:
        return ucli.obter(db, id)
    except Exception as e:
        c, m = errmap(e)
        raise HTTPException(c, m) from e


@router.put("/{id}", response_model=ClienteOut, dependencies=[Depends(require_admin)])
def p(id: int, body: ClienteIn, db: Session = Depends(get_session)) -> ClienteOut:
    try:
        r = ucli.atualizar(db, id, body)
        db.commit()
        return r
    except Exception as e:
        db.rollback()
        c, m = errmap(e)
        raise HTTPException(c, m) from e


@router.delete("/{id}", status_code=204, response_class=Response, dependencies=[Depends(require_admin)])
def d(id: int, db: Session = Depends(get_session)) -> None:
    try:
        ucli.deletar(db, id)
        db.commit()
    except Exception as e:
        db.rollback()
        c, m = errmap(e)
        raise HTTPException(c, m) from e
