from __future__ import annotations

from app.application.ports.email_notifier import IEmailNotifier
from app.domain.entities import OrdemServico
from app.domain.repositories import IClienteRepository
from app.domain.services.ordem_servico_listagem import descricao_status


class OsStatusNotifier:
    def __init__(
        self,
        clientes: IClienteRepository,
        email: IEmailNotifier,
    ) -> None:
        self._clientes = clientes
        self._email = email

    def notificar_mudanca(self, os_: OrdemServico) -> None:
        if os_.id is None:
            return
        cli = self._clientes.get_by_id(os_.cliente_id)
        if cli is None:
            return
        contato = cli.contato.strip()
        if "@" not in contato:
            return
        self._email.enviar_atualizacao_os(
            destinatario=contato,
            os_id=os_.id,
            status_descricao=descricao_status(os_.status),
            referencia_externa=os_.referencia_externa,
        )
