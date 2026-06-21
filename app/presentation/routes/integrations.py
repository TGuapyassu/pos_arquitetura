from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.application.dtos.ordem_dto import OrcamentoDecisaoIn, OrdemStatusOut, WebhookStatusIn
from app.application.use_cases.ordem_servico import (
    AtualizarStatusViaIntegracao,
    DecidirOrcamentoExterno,
)
from app.infrastructure.database import get_session
from app.presentation.composition import (
    get_atualizar_status_integracao,
    get_decidir_orcamento_externo,
    require_webhook_key,
)
from app.presentation.transaction import run_in_transaction

router = APIRouter(prefix="/integrations", tags=["integrações"])


@router.post(
    "/os/{id}/orcamento",
    response_model=OrdemStatusOut,
    dependencies=[Depends(require_webhook_key)],
)
def decidir_orcamento_externo(
    id: int,
    body: OrcamentoDecisaoIn,
    db: Session = Depends(get_session),
    use_case: DecidirOrcamentoExterno = Depends(get_decidir_orcamento_externo),
) -> OrdemStatusOut:
    return run_in_transaction(db, lambda: use_case.execute(id, body))


@router.post(
    "/os/{id}/status",
    response_model=OrdemStatusOut,
    dependencies=[Depends(require_webhook_key)],
)
def atualizar_status_via_integracao(
    id: int,
    body: WebhookStatusIn,
    db: Session = Depends(get_session),
    use_case: AtualizarStatusViaIntegracao = Depends(get_atualizar_status_integracao),
) -> OrdemStatusOut:
    return run_in_transaction(db, lambda: use_case.execute(id, body))
