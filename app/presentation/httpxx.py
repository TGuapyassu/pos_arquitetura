"""Mapeia exceções de domínio / aplicação para códigos HTTP (camada de apresentação)."""

from __future__ import annotations

from app.domain.exceptions import (
    AprovacaoNecessariaError,
    AutenticacaoError,
    ConflictError,
    DomainError,
    EstoqueInsuficienteError,
    NotFoundError,
    TransicaoStatusInvalidaError,
)


def errmap(e: Exception) -> tuple[int, str]:
    if isinstance(e, NotFoundError):
        return 404, str(e)
    if isinstance(e, (AutenticacaoError,)):
        return 401, str(e)
    if isinstance(e, EstoqueInsuficienteError):
        return 409, str(e)
    if isinstance(e, ConflictError):
        return 409, str(e)
    if isinstance(e, (AprovacaoNecessariaError, TransicaoStatusInvalidaError)):
        return 400, str(e)
    if isinstance(e, DomainError):
        return 400, str(e)
    return 500, "Erro interno do servidor"
