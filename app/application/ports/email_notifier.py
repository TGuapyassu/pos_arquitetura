from __future__ import annotations

from typing import Protocol


class IEmailNotifier(Protocol):
    def enviar_atualizacao_os(
        self,
        destinatario: str,
        os_id: int,
        status_descricao: str,
        referencia_externa: str | None = None,
    ) -> None: ...
