from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.application.dtos.peca_dto import PecaEstoqueIn, PecaIn, PecaOut
from app.application.use_cases.peca import PecaService
from app.infrastructure.database import get_session
from app.presentation.composition import get_peca_service
from app.presentation.dependencies import require_admin
from app.presentation.transaction import handle_domain_errors, run_in_transaction

router = APIRouter(prefix="/pecas", tags=["peças"])


@router.post("", response_model=PecaOut, status_code=201, dependencies=[Depends(require_admin)])
def criar_peca(
    body: PecaIn,
    db: Session = Depends(get_session),
    service: PecaService = Depends(get_peca_service),
) -> PecaOut:
    return run_in_transaction(db, lambda: service.criar(body))


@router.get("", response_model=list[PecaOut], dependencies=[Depends(require_admin)])
def listar_pecas(
    service: PecaService = Depends(get_peca_service),
) -> list[PecaOut]:
    return service.listar()


@router.get("/{id}", response_model=PecaOut, dependencies=[Depends(require_admin)])
def obter_peca(
    id: int,
    service: PecaService = Depends(get_peca_service),
) -> PecaOut:
    return handle_domain_errors(lambda: service.obter(id))


@router.put("/{id}", response_model=PecaOut, dependencies=[Depends(require_admin)])
def atualizar_peca(
    id: int,
    body: PecaIn,
    db: Session = Depends(get_session),
    service: PecaService = Depends(get_peca_service),
) -> PecaOut:
    return run_in_transaction(db, lambda: service.atualizar(id, body))


@router.patch("/{id}/estoque", response_model=PecaOut, dependencies=[Depends(require_admin)])
def atualizar_estoque_peca(
    id: int,
    body: PecaEstoqueIn,
    db: Session = Depends(get_session),
    service: PecaService = Depends(get_peca_service),
) -> PecaOut:
    return run_in_transaction(db, lambda: service.atualizar_estoque(id, body))


@router.delete(
    "/{id}",
    status_code=204,
    response_class=Response,
    dependencies=[Depends(require_admin)],
)
def deletar_peca(
    id: int,
    db: Session = Depends(get_session),
    service: PecaService = Depends(get_peca_service),
) -> None:
    run_in_transaction(db, lambda: service.deletar(id))
