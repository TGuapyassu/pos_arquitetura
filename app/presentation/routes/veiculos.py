from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.application.dtos import VeiculoIn, VeiculoOut
from app.application.use_cases import veiculo as uve
from app.infrastructure.database import get_session
from app.presentation.dependencies import require_admin
from app.presentation.httpxx import errmap

router = APIRouter(prefix="/veiculos", tags=["veículos"])


@router.post("", response_model=VeiculoOut, status_code=201, dependencies=[Depends(require_admin)])
def c(body: VeiculoIn, db: Session = Depends(get_session)) -> VeiculoOut:
    try:
        r = uve.criar(db, body)
        db.commit()
        return r
    except Exception as e:
        db.rollback()
        c, m = errmap(e)
        raise HTTPException(c, m) from e


@router.get("", response_model=list[VeiculoOut], dependencies=[Depends(require_admin)])
def ls(
    db: Session = Depends(get_session),
    cliente_id: Optional[int] = None,
) -> list[VeiculoOut]:
    if cliente_id is not None:
        try:
            return uve.listar_por_cliente(db, cliente_id)
        except Exception as e:
            c, m = errmap(e)
            raise HTTPException(c, m) from e
    return uve.listar(db)


@router.get("/{id}", response_model=VeiculoOut, dependencies=[Depends(require_admin)])
def g(id: int, db: Session = Depends(get_session)) -> VeiculoOut:
    try:
        return uve.obter(db, id)
    except Exception as e:
        c, m = errmap(e)
        raise HTTPException(c, m) from e


@router.put("/{id}", response_model=VeiculoOut, dependencies=[Depends(require_admin)])
def p(id: int, body: VeiculoIn, db: Session = Depends(get_session)) -> VeiculoOut:
    try:
        r = uve.atualizar(db, id, body)
        db.commit()
        return r
    except Exception as e:
        db.rollback()
        c, m = errmap(e)
        raise HTTPException(c, m) from e


@router.delete("/{id}", status_code=204, response_class=Response, dependencies=[Depends(require_admin)])
def d(id: int, db: Session = Depends(get_session)) -> None:
    try:
        uve.deletar(db, id)
        db.commit()
    except Exception as e:
        db.rollback()
        c, m = errmap(e)
        raise HTTPException(c, m) from e
