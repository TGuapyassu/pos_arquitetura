from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.application.dtos import VeiculoIn, VeiculoOut
from app.application.use_cases.veiculo import VeiculoService
from app.infrastructure.database import get_session
from app.presentation.composition import get_veiculo_service
from app.presentation.dependencies import require_admin
from app.presentation.transaction import handle_domain_errors, run_in_transaction

router = APIRouter(prefix="/veiculos", tags=["veículos"])


@router.post("", response_model=VeiculoOut, status_code=201, dependencies=[Depends(require_admin)])
def criar_veiculo(
    body: VeiculoIn,
    db: Session = Depends(get_session),
    service: VeiculoService = Depends(get_veiculo_service),
) -> VeiculoOut:
    return run_in_transaction(db, lambda: service.criar(body))


@router.get("", response_model=list[VeiculoOut], dependencies=[Depends(require_admin)])
def listar_veiculos(
    service: VeiculoService = Depends(get_veiculo_service),
    cliente_id: Optional[int] = None,
) -> list[VeiculoOut]:
    if cliente_id is not None:
        return handle_domain_errors(lambda: service.listar_por_cliente(cliente_id))
    return service.listar()


@router.get("/{id}", response_model=VeiculoOut, dependencies=[Depends(require_admin)])
def obter_veiculo(
    id: int,
    service: VeiculoService = Depends(get_veiculo_service),
) -> VeiculoOut:
    return handle_domain_errors(lambda: service.obter(id))


@router.put("/{id}", response_model=VeiculoOut, dependencies=[Depends(require_admin)])
def atualizar_veiculo(
    id: int,
    body: VeiculoIn,
    db: Session = Depends(get_session),
    service: VeiculoService = Depends(get_veiculo_service),
) -> VeiculoOut:
    return run_in_transaction(db, lambda: service.atualizar(id, body))


@router.delete(
    "/{id}",
    status_code=204,
    response_class=Response,
    dependencies=[Depends(require_admin)],
)
def deletar_veiculo(
    id: int,
    db: Session = Depends(get_session),
    service: VeiculoService = Depends(get_veiculo_service),
) -> None:
    run_in_transaction(db, lambda: service.deletar(id))
