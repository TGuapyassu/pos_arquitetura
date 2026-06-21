from __future__ import annotations

from app.application.services.os_status_notifier import OsStatusNotifier
from app.domain.entities import Cliente, OrdemServico
from app.domain.enums import OrdemServicoStatus


class SpyEmailNotifier:
    def __init__(self) -> None:
        self.chamadas: list[tuple[str, int, str]] = []

    def enviar_atualizacao_os(
        self,
        destinatario: str,
        os_id: int,
        status_descricao: str,
        referencia_externa: str | None = None,
    ) -> None:
        self.chamadas.append((destinatario, os_id, status_descricao))


def test_notifier_envia_email_quando_contato_tem_arroba():
    spy = SpyEmailNotifier()
    clientes = _FakeClienteRepo(
        Cliente(id=1, nome="Maria", contato="maria@test.com", cpf_cnpj="52998224725")
    )
    notifier = OsStatusNotifier(clientes, spy)
    os_ = OrdemServico(
        id=10,
        cliente_id=1,
        veiculo_id=1,
        status=OrdemServicoStatus.EM_DIAGNOSTICO,
    )
    notifier.notificar_mudanca(os_)
    assert spy.chamadas == [("maria@test.com", 10, "Diagnóstico")]


def test_notifier_ignora_contato_sem_email():
    spy = SpyEmailNotifier()
    clientes = _FakeClienteRepo(
        Cliente(id=1, nome="Maria", contato="(11)99999-9999", cpf_cnpj="52998224725")
    )
    notifier = OsStatusNotifier(clientes, spy)
    os_ = OrdemServico(
        id=10,
        cliente_id=1,
        veiculo_id=1,
        status=OrdemServicoStatus.RECEBIDA,
    )
    notifier.notificar_mudanca(os_)
    assert spy.chamadas == []


class _FakeClienteRepo:
    def __init__(self, cliente: Cliente) -> None:
        self._cliente = cliente

    def get_by_id(self, id: int):
        return self._cliente if id == self._cliente.id else None
