from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.application.dtos.ordem_dto import (
    OrdemAberturaOut,
    OrdemCreateIn,
    OrdemOut,
    OrdemUpdateStatusIn,
)
from app.application.use_cases.ordem_servico import (
    AprovarOrdemServico,
    AtualizarStatusOrdem,
    CriarOrdemServico,
    ListarOrdensServicoAtivas,
    ObterOrdemServico,
)
from app.infrastructure.database import get_session
from app.presentation.composition import (
    get_aprovar_ordem_servico,
    get_atualizar_status_ordem,
    get_criar_ordem_servico,
    get_listar_ordens_servico_ativas,
    get_obter_ordem_servico,
)
from app.presentation.dependencies import require_admin
from app.presentation.transaction import handle_domain_errors, run_in_transaction

router = APIRouter(prefix="/os", tags=["ordem de serviço"])


@router.post(
    "",
    response_model=OrdemAberturaOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def criar_ordem_servico(
    body: OrdemCreateIn,
    db: Session = Depends(get_session),
    use_case: CriarOrdemServico = Depends(get_criar_ordem_servico),
) -> OrdemAberturaOut:
    return run_in_transaction(db, lambda: use_case.execute(body))


@router.get("/{id}", response_model=OrdemOut, dependencies=[Depends(require_admin)])
def obter_ordem_servico(
    id: int,
    use_case: ObterOrdemServico = Depends(get_obter_ordem_servico),
) -> OrdemOut:
    return handle_domain_errors(lambda: use_case.execute(id))


@router.get("", response_model=list[OrdemOut], dependencies=[Depends(require_admin)])
def listar_ordens_servico(
    use_case: ListarOrdensServicoAtivas = Depends(get_listar_ordens_servico_ativas),
) -> list[OrdemOut]:
    return use_case.execute()


@router.patch("/{id}/status", response_model=OrdemOut, dependencies=[Depends(require_admin)])
def atualizar_status_ordem(
    id: int,
    body: OrdemUpdateStatusIn,
    db: Session = Depends(get_session),
    use_case: AtualizarStatusOrdem = Depends(get_atualizar_status_ordem),
) -> OrdemOut:
    return run_in_transaction(db, lambda: use_case.execute(id, body))


@router.post("/{id}/aprovar", response_model=OrdemOut, dependencies=[Depends(require_admin)])
def aprovar_ordem_servico(
    id: int,
    db: Session = Depends(get_session),
    use_case: AprovarOrdemServico = Depends(get_aprovar_ordem_servico),
) -> OrdemOut:
    return run_in_transaction(db, lambda: use_case.execute(id))
