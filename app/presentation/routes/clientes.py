from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.application.dtos import ClienteIn, ClienteOut
from app.application.use_cases.cliente import ClienteService
from app.infrastructure.database import get_session
from app.presentation.composition import get_cliente_service
from app.presentation.dependencies import require_admin
from app.presentation.transaction import handle_domain_errors, run_in_transaction

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.post("", response_model=ClienteOut, status_code=201, dependencies=[Depends(require_admin)])
def criar_cliente(
    body: ClienteIn,
    db: Session = Depends(get_session),
    service: ClienteService = Depends(get_cliente_service),
) -> ClienteOut:
    return run_in_transaction(db, lambda: service.criar(body))


@router.get("", response_model=list[ClienteOut], dependencies=[Depends(require_admin)])
def listar_clientes(
    service: ClienteService = Depends(get_cliente_service),
) -> list[ClienteOut]:
    return service.listar()


@router.get("/{id}", response_model=ClienteOut, dependencies=[Depends(require_admin)])
def obter_cliente(
    id: int,
    service: ClienteService = Depends(get_cliente_service),
) -> ClienteOut:
    return handle_domain_errors(lambda: service.obter(id))


@router.put("/{id}", response_model=ClienteOut, dependencies=[Depends(require_admin)])
def atualizar_cliente(
    id: int,
    body: ClienteIn,
    db: Session = Depends(get_session),
    service: ClienteService = Depends(get_cliente_service),
) -> ClienteOut:
    return run_in_transaction(db, lambda: service.atualizar(id, body))


@router.delete(
    "/{id}",
    status_code=204,
    response_class=Response,
    dependencies=[Depends(require_admin)],
)
def deletar_cliente(
    id: int,
    db: Session = Depends(get_session),
    service: ClienteService = Depends(get_cliente_service),
) -> None:
    run_in_transaction(db, lambda: service.deletar(id))
