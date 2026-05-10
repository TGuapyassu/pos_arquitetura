from __future__ import annotations

from enum import Enum


class OrdemServicoStatus(str, Enum):
    """Status possíveis da Ordem de Serviço (state machine no domínio)."""

    RECEBIDA = "RECEBIDA"
    EM_DIAGNOSTICO = "EM_DIAGNOSTICO"
    AGUARDANDO_APROVACAO = "AGUARDANDO_APROVACAO"
    EM_EXECUCAO = "EM_EXECUCAO"
    FINALIZADA = "FINALIZADA"
    ENTREGUE = "ENTREGUE"
