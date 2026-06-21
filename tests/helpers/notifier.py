from __future__ import annotations

from app.domain.entities import OrdemServico


class NoOpOsStatusNotifier:
    def notificar_mudanca(self, os_: OrdemServico) -> None:
        return None
