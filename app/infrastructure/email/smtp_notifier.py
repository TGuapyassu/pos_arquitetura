from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from app.infrastructure.config import get_settings

log = logging.getLogger(__name__)


class ConsoleEmailNotifier:
    def enviar_atualizacao_os(
        self,
        destinatario: str,
        os_id: int,
        status_descricao: str,
        referencia_externa: str | None = None,
    ) -> None:
        log.info(
            "E-mail OS #%s -> %s | status=%s ref=%s",
            os_id,
            destinatario,
            status_descricao,
            referencia_externa,
        )


class SmtpEmailNotifier:
    def enviar_atualizacao_os(
        self,
        destinatario: str,
        os_id: int,
        status_descricao: str,
        referencia_externa: str | None = None,
    ) -> None:
        s = get_settings()
        msg = EmailMessage()
        msg["Subject"] = f"Atualização da OS #{os_id}"
        msg["From"] = s.email_from
        msg["To"] = destinatario
        corpo = (
            f"Sua ordem de serviço #{os_id} foi atualizada.\n\n"
            f"Status atual: {status_descricao}\n"
        )
        if referencia_externa:
            corpo += f"Referência: {referencia_externa}\n"
        msg.set_content(corpo)
        with smtplib.SMTP(s.smtp_host, s.smtp_port, timeout=15) as smtp:
            if s.smtp_user and s.smtp_password:
                smtp.starttls()
                smtp.login(s.smtp_user, s.smtp_password)
            smtp.send_message(msg)


def build_email_notifier() -> ConsoleEmailNotifier | SmtpEmailNotifier:
    s = get_settings()
    if not s.email_enabled:
        return ConsoleEmailNotifier()
    return SmtpEmailNotifier()
