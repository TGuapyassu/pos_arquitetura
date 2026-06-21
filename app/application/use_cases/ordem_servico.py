from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from app.application.dtos import (
    OrdemAberturaOut,
    OrdemCreateIn,
    OrdemOut,
    OrdemStatusOut,
    OrdemUpdateStatusIn,
    OrcamentoDecisaoIn,
    WebhookStatusIn,
)
from app.application.dtos.ordem_dto import OrdemPublicaOut
from app.application.mapping.dto_mappers import ordem_to_out, ordem_to_publica, ordem_to_status
from app.application.services.os_status_notifier import OsStatusNotifier
from app.domain.entities import (
    ItemPecaOS,
    ItemServicoOS,
    OrdemServico,
    Peca,
)
from app.domain.exceptions import ConflictError, NotFoundError
from app.domain.repositories import (
    IClienteRepository,
    IOrdemServicoRepository,
    IPecaRepository,
    IServicoOficinaRepository,
    IVeiculoRepository,
)
from app.domain.services.ordem_servico_listagem import ordenar_ordens_ativas
from app.domain.value_objects import CpfCnpj, Placa


class CriarOrdemServico:
    def __init__(
        self,
        clientes: IClienteRepository,
        veiculos: IVeiculoRepository,
        servicos: IServicoOficinaRepository,
        pecas: IPecaRepository,
        ordens: IOrdemServicoRepository,
    ) -> None:
        self._clientes = clientes
        self._veiculos = veiculos
        self._servicos = servicos
        self._pecas = pecas
        self._ordens = ordens

    def execute(self, body: OrdemCreateIn) -> OrdemAberturaOut:
        self._validar_cliente_e_veiculo(body)
        it_s = self._montar_itens_servico(body)
        it_p = self._montar_itens_peca(body)
        os_ = OrdemServico.abrir_nova(cliente_id=body.cliente_id, veiculo_id=body.veiculo_id)
        os_.atribuir_itens(it_s, it_p)
        self._ordens.add(os_)
        return OrdemAberturaOut(id=os_.id or 0)

    def _validar_cliente_e_veiculo(self, body: OrdemCreateIn) -> None:
        cli = self._clientes.get_by_id(body.cliente_id)
        if not cli:
            raise NotFoundError("Cliente não encontrado.")
        _ = CpfCnpj.parse(cli.cpf_cnpj)

        v = self._veiculos.get_by_id(body.veiculo_id)
        if not v:
            raise NotFoundError("Veículo não encontrado.")
        _ = Placa.parse(v.placa)
        if v.cliente_id != body.cliente_id:
            raise ConflictError("Veículo não pertence ao cliente informado.")

    def _montar_itens_servico(self, body: OrdemCreateIn) -> list[ItemServicoOS]:
        itens: list[ItemServicoOS] = []
        for lin in body.servicos:
            so = self._servicos.get_by_id(lin.servico_id)
            if not so:
                raise NotFoundError(f"Serviço id={lin.servico_id} não encontrado.")
            itens.append(
                ItemServicoOS(
                    servico_id=so.id or lin.servico_id,
                    quantidade=lin.quantidade,
                    preco_unitario=Decimal(so.preco).quantize(Decimal("0.01")),
                )
            )
        return itens

    def _montar_itens_peca(self, body: OrdemCreateIn) -> list[ItemPecaOS]:
        ag_p: dict[int, int] = defaultdict(int)
        for lin in body.pecas:
            ag_p[lin.peca_id] += lin.quantidade

        peca_map: dict[int, Peca] = {}
        for pid, q in ag_p.items():
            p = self._pecas.get_by_id(pid)
            if not p:
                raise NotFoundError(f"Peça id={pid} não encontrada.")
            p.reservar_ou_baixar(q)
            peca_map[pid] = p
            self._pecas.update(p)

        itens: list[ItemPecaOS] = []
        for lin in body.pecas:
            p = peca_map[lin.peca_id]
            itens.append(
                ItemPecaOS(
                    peca_id=p.id or lin.peca_id,
                    quantidade=lin.quantidade,
                    preco_unitario=Decimal(p.preco).quantize(Decimal("0.01")),
                )
            )
        return itens


class ListarOrdensServicoAtivas:
    def __init__(self, ordens: IOrdemServicoRepository) -> None:
        self._ordens = ordens

    def execute(self) -> list[OrdemOut]:
        ativas = ordenar_ordens_ativas(self._ordens.listar_ativas())
        return [ordem_to_out(o) for o in ativas]


class ObterOrdemServico:
    def __init__(self, ordens: IOrdemServicoRepository) -> None:
        self._ordens = ordens

    def execute(self, id: int) -> OrdemOut:
        o = self._ordens.get_by_id(id)
        if o is None:
            raise NotFoundError("OS não encontrada.")
        return ordem_to_out(o)


class ObterStatusOrdem:
    def __init__(self, ordens: IOrdemServicoRepository) -> None:
        self._ordens = ordens

    def execute(self, id: int) -> OrdemStatusOut:
        o = self._ordens.get_by_id(id)
        if o is None:
            raise NotFoundError("OS não encontrada.")
        return ordem_to_status(o)


class ObterOrdemPublica:
    def __init__(self, ordens: IOrdemServicoRepository) -> None:
        self._ordens = ordens

    def execute(self, id: int) -> OrdemPublicaOut:
        o = self._ordens.get_by_id(id)
        if o is None:
            raise NotFoundError("OS não encontrada.")
        return ordem_to_publica(o)


class AtualizarStatusOrdem:
    def __init__(
        self,
        ordens: IOrdemServicoRepository,
        notifier: OsStatusNotifier,
    ) -> None:
        self._ordens = ordens
        self._notifier = notifier

    def execute(self, id: int, body: OrdemUpdateStatusIn) -> OrdemOut:
        o = self._ordens.get_by_id(id)
        if o is None:
            raise NotFoundError("OS não encontrada.")
        o.transicionar_por_patch(body.status)
        self._ordens.update(o)
        atualizada = self._ordens.get_by_id(id) or o
        self._notifier.notificar_mudanca(atualizada)
        return ordem_to_out(atualizada)


class AprovarOrdemServico:
    def __init__(
        self,
        ordens: IOrdemServicoRepository,
        notifier: OsStatusNotifier,
    ) -> None:
        self._ordens = ordens
        self._notifier = notifier

    def execute(self, id: int, referencia_externa: str | None = None) -> OrdemOut:
        o = self._ordens.get_by_id(id)
        if o is None:
            raise NotFoundError("OS não encontrada.")
        o.aprovar_orcamento(referencia_externa=referencia_externa)
        self._ordens.update(o)
        atualizada = self._ordens.get_by_id(id) or o
        self._notifier.notificar_mudanca(atualizada)
        return ordem_to_out(atualizada)


class DecidirOrcamentoExterno:
    def __init__(
        self,
        ordens: IOrdemServicoRepository,
        notifier: OsStatusNotifier,
    ) -> None:
        self._ordens = ordens
        self._notifier = notifier

    def execute(self, id: int, body: OrcamentoDecisaoIn) -> OrdemStatusOut:
        o = self._ordens.get_by_id(id)
        if o is None:
            raise NotFoundError("OS não encontrada.")
        if body.aprovado:
            o.aprovar_orcamento(referencia_externa=body.referencia_externa)
        else:
            o.recusar_orcamento(referencia_externa=body.referencia_externa)
        self._ordens.update(o)
        atualizada = self._ordens.get_by_id(id) or o
        self._notifier.notificar_mudanca(atualizada)
        return ordem_to_status(atualizada)


class AtualizarStatusViaIntegracao:
    def __init__(
        self,
        ordens: IOrdemServicoRepository,
        notifier: OsStatusNotifier,
    ) -> None:
        self._ordens = ordens
        self._notifier = notifier

    def execute(self, id: int, body: WebhookStatusIn) -> OrdemStatusOut:
        o = self._ordens.get_by_id(id)
        if o is None:
            raise NotFoundError("OS não encontrada.")
        o.transicionar_por_patch(body.status)
        if body.referencia_externa:
            o.referencia_externa = body.referencia_externa
        self._ordens.update(o)
        atualizada = self._ordens.get_by_id(id) or o
        self._notifier.notificar_mudanca(atualizada)
        return ordem_to_status(atualizada)
