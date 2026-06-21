from fastapi import APIRouter, Depends

from app.application.dtos.ordem_dto import OrdemPublicaOut, OrdemStatusOut
from app.application.use_cases.ordem_servico import ObterOrdemPublica, ObterStatusOrdem
from app.presentation.composition import get_obter_ordem_publica, get_obter_status_ordem
from app.presentation.transaction import handle_domain_errors

router = APIRouter(prefix="/public", tags=["público"])


@router.get(
    "/ordens-servico/{id}",
    response_model=OrdemPublicaOut,
    summary="Consulta pública de OS (cliente) — sem autenticação",
)
def consultar_ordem_publica(
    id: int,
    use_case: ObterOrdemPublica = Depends(get_obter_ordem_publica),
) -> OrdemPublicaOut:
    return handle_domain_errors(lambda: use_case.execute(id))


@router.get(
    "/ordens-servico/{id}/status",
    response_model=OrdemStatusOut,
    summary="Consulta pública do status da OS — sem autenticação",
)
def consultar_status_ordem(
    id: int,
    use_case: ObterStatusOrdem = Depends(get_obter_status_ordem),
) -> OrdemStatusOut:
    return handle_domain_errors(lambda: use_case.execute(id))
