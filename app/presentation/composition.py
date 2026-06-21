from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.application.services.os_status_notifier import OsStatusNotifier
from app.application.use_cases.auth import LoginUseCase
from app.application.use_cases.cliente import ClienteService
from app.application.use_cases.ordem_servico import (
    AprovarOrdemServico,
    AtualizarStatusOrdem,
    AtualizarStatusViaIntegracao,
    CriarOrdemServico,
    DecidirOrcamentoExterno,
    ListarOrdensServicoAtivas,
    ObterOrdemPublica,
    ObterOrdemServico,
    ObterStatusOrdem,
)
from app.application.use_cases.peca import PecaService
from app.application.use_cases.servico_oficina import ServicoOficinaService
from app.application.use_cases.veiculo import VeiculoService
from app.domain.repositories import (
    IClienteRepository,
    IOrdemServicoRepository,
    IPecaRepository,
    IServicoOficinaRepository,
    IUsuarioRepository,
    IVeiculoRepository,
)
from app.infrastructure.config import get_settings
from app.infrastructure.database import get_session
from app.infrastructure.email.smtp_notifier import build_email_notifier
from app.infrastructure.repositories.sqlalchemy_cliente import SqlAlchemyClienteRepository
from app.infrastructure.repositories.sqlalchemy_ordem_servico import SqlAlchemyOrdemServicoRepository
from app.infrastructure.repositories.sqlalchemy_peca import SqlAlchemyPecaRepository
from app.infrastructure.repositories.sqlalchemy_servico import SqlAlchemyServicoOficinaRepository
from app.infrastructure.repositories.sqlalchemy_usuario import SqlAlchemyUsuarioRepository
from app.infrastructure.repositories.sqlalchemy_veiculo import SqlAlchemyVeiculoRepository
from app.infrastructure.security import create_token, verify_password


@dataclass(frozen=True)
class Repositories:
    clientes: IClienteRepository
    veiculos: IVeiculoRepository
    servicos: IServicoOficinaRepository
    pecas: IPecaRepository
    ordens: IOrdemServicoRepository
    usuarios: IUsuarioRepository


class JwtAuthGateway:
    def verify_password(self, plain: str, hashed: str) -> bool:
        return verify_password(plain, hashed)

    def create_token(self, user_id: int, email: str, is_admin: bool) -> str:
        return create_token(user_id=user_id, email=email, is_admin=is_admin)


_auth_gateway = JwtAuthGateway()
_email_notifier = build_email_notifier()


def build_repositories(session: Session) -> Repositories:
    return Repositories(
        clientes=SqlAlchemyClienteRepository(session),
        veiculos=SqlAlchemyVeiculoRepository(session),
        servicos=SqlAlchemyServicoOficinaRepository(session),
        pecas=SqlAlchemyPecaRepository(session),
        ordens=SqlAlchemyOrdemServicoRepository(session),
        usuarios=SqlAlchemyUsuarioRepository(session),
    )


def get_repositories(db: Session = Depends(get_session)) -> Repositories:
    return build_repositories(db)


def get_os_status_notifier(repos: Repositories = Depends(get_repositories)) -> OsStatusNotifier:
    return OsStatusNotifier(repos.clientes, _email_notifier)


def require_webhook_key(x_webhook_key: str | None = Header(default=None, alias="X-Webhook-Key")) -> None:
    expected = get_settings().webhook_api_key
    if not x_webhook_key or x_webhook_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave de webhook inválida ou ausente.",
        )


def get_cliente_service(repos: Repositories = Depends(get_repositories)) -> ClienteService:
    return ClienteService(repos.clientes)


def get_veiculo_service(repos: Repositories = Depends(get_repositories)) -> VeiculoService:
    return VeiculoService(repos.veiculos, repos.clientes)


def get_servico_service(repos: Repositories = Depends(get_repositories)) -> ServicoOficinaService:
    return ServicoOficinaService(repos.servicos)


def get_peca_service(repos: Repositories = Depends(get_repositories)) -> PecaService:
    return PecaService(repos.pecas)


def get_login_use_case(repos: Repositories = Depends(get_repositories)) -> LoginUseCase:
    return LoginUseCase(repos.usuarios, _auth_gateway)


def get_criar_ordem_servico(repos: Repositories = Depends(get_repositories)) -> CriarOrdemServico:
    return CriarOrdemServico(
        repos.clientes,
        repos.veiculos,
        repos.servicos,
        repos.pecas,
        repos.ordens,
    )


def get_listar_ordens_servico_ativas(
    repos: Repositories = Depends(get_repositories),
) -> ListarOrdensServicoAtivas:
    return ListarOrdensServicoAtivas(repos.ordens)


def get_obter_ordem_servico(repos: Repositories = Depends(get_repositories)) -> ObterOrdemServico:
    return ObterOrdemServico(repos.ordens)


def get_obter_status_ordem(repos: Repositories = Depends(get_repositories)) -> ObterStatusOrdem:
    return ObterStatusOrdem(repos.ordens)


def get_obter_ordem_publica(repos: Repositories = Depends(get_repositories)) -> ObterOrdemPublica:
    return ObterOrdemPublica(repos.ordens)


def get_atualizar_status_ordem(
    repos: Repositories = Depends(get_repositories),
    notifier: OsStatusNotifier = Depends(get_os_status_notifier),
) -> AtualizarStatusOrdem:
    return AtualizarStatusOrdem(repos.ordens, notifier)


def get_aprovar_ordem_servico(
    repos: Repositories = Depends(get_repositories),
    notifier: OsStatusNotifier = Depends(get_os_status_notifier),
) -> AprovarOrdemServico:
    return AprovarOrdemServico(repos.ordens, notifier)


def get_decidir_orcamento_externo(
    repos: Repositories = Depends(get_repositories),
    notifier: OsStatusNotifier = Depends(get_os_status_notifier),
) -> DecidirOrcamentoExterno:
    return DecidirOrcamentoExterno(repos.ordens, notifier)


def get_atualizar_status_integracao(
    repos: Repositories = Depends(get_repositories),
    notifier: OsStatusNotifier = Depends(get_os_status_notifier),
) -> AtualizarStatusViaIntegracao:
    return AtualizarStatusViaIntegracao(repos.ordens, notifier)
