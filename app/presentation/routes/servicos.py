from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.application.dtos import ServicoIn, ServicoOut
from app.application.use_cases.servico_oficina import ServicoOficinaService
from app.infrastructure.database import get_session
from app.presentation.composition import get_servico_service
from app.presentation.dependencies import require_admin
from app.presentation.transaction import handle_domain_errors, run_in_transaction

router = APIRouter(prefix="/servicos", tags=["serviços"])


@router.post("", response_model=ServicoOut, status_code=201, dependencies=[Depends(require_admin)])
def criar_servico(
    body: ServicoIn,
    db: Session = Depends(get_session),
    service: ServicoOficinaService = Depends(get_servico_service),
) -> ServicoOut:
    return run_in_transaction(db, lambda: service.criar(body))


@router.get("", response_model=list[ServicoOut], dependencies=[Depends(require_admin)])
def listar_servicos(
    service: ServicoOficinaService = Depends(get_servico_service),
) -> list[ServicoOut]:
    return service.listar()


@router.get("/{id}", response_model=ServicoOut, dependencies=[Depends(require_admin)])
def obter_servico(
    id: int,
    service: ServicoOficinaService = Depends(get_servico_service),
) -> ServicoOut:
    return handle_domain_errors(lambda: service.obter(id))


@router.put("/{id}", response_model=ServicoOut, dependencies=[Depends(require_admin)])
def atualizar_servico(
    id: int,
    body: ServicoIn,
    db: Session = Depends(get_session),
    service: ServicoOficinaService = Depends(get_servico_service),
) -> ServicoOut:
    return run_in_transaction(db, lambda: service.atualizar(id, body))


@router.delete(
    "/{id}",
    status_code=204,
    response_class=Response,
    dependencies=[Depends(require_admin)],
)
def deletar_servico(
    id: int,
    db: Session = Depends(get_session),
    service: ServicoOficinaService = Depends(get_servico_service),
) -> None:
    run_in_transaction(db, lambda: service.deletar(id))
