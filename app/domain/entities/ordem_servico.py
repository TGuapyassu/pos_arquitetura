from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from app.domain.enums import OrdemServicoStatus
from app.domain.services.ordem_servico_status import (
    transicao_apos_aprovacao,
    transicao_apos_recusa,
    transicao_status_via_patch_permitida,
)


@dataclass
class ItemServicoOS:
    servico_id: int
    quantidade: int
    preco_unitario: Decimal

    def subtotal(self) -> Decimal:
        return (self.preco_unitario * Decimal(self.quantidade)).quantize(
            Decimal("0.01")
        )


@dataclass
class ItemPecaOS:
    peca_id: int
    quantidade: int
    preco_unitario: Decimal

    def subtotal(self) -> Decimal:
        return (self.preco_unitario * Decimal(self.quantidade)).quantize(
            Decimal("0.01")
        )


@dataclass
class OrdemServico:
    """Raiz do agregado: status, itens e cálculo de orçamento."""

    cliente_id: int
    veiculo_id: int
    status: OrdemServicoStatus
    itens_servico: list[ItemServicoOS] = field(default_factory=list)
    itens_peca: list[ItemPecaOS] = field(default_factory=list)
    id: Optional[int] = None
    valor_total: Optional[Decimal] = None
    aprovada_em: Optional[datetime] = None
    recusada_em: Optional[datetime] = None
    referencia_externa: Optional[str] = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    data_finalizacao: Optional[datetime] = None
    data_entrega: Optional[datetime] = None

    @staticmethod
    def abrir_nova(cliente_id: int, veiculo_id: int) -> "OrdemServico":
        return OrdemServico(
            cliente_id=cliente_id,
            veiculo_id=veiculo_id,
            status=OrdemServicoStatus.RECEBIDA,
        )

    def calcular_valor_total(self) -> Decimal:
        t = sum((i.subtotal() for i in self.itens_servico), start=Decimal("0"))
        t += sum((i.subtotal() for i in self.itens_peca), start=Decimal("0"))
        return t.quantize(Decimal("0.01"))

    def _atualizar_valor_total_persistido(self) -> None:
        self.valor_total = self.calcular_valor_total()

    def atribuir_itens(
        self, servicos: list[ItemServicoOS], pecas: list[ItemPecaOS]
    ) -> None:
        self.itens_servico = list(servicos)
        self.itens_peca = list(pecas)
        self._atualizar_valor_total_persistido()

    def alinhar_valor_total_ao_carregar(self) -> None:
        if self.valor_total is None and (self.itens_servico or self.itens_peca):
            self._atualizar_valor_total_persistido()

    def transicionar_por_patch(self, destino: OrdemServicoStatus) -> None:
        if destino == self.status:
            return
        transicao_status_via_patch_permitida(self.status, destino)
        self._anexar_datas_se_aplicavel(destino)
        self.status = destino
        self.updated_at = datetime.now(timezone.utc)

    def aprovar_orcamento(self, referencia_externa: str | None = None) -> None:
        novo = transicao_apos_aprovacao(self.status)
        self.aprovada_em = datetime.now(timezone.utc)
        if referencia_externa:
            self.referencia_externa = referencia_externa
        self._anexar_datas_se_aplicavel(novo)
        self.status = novo
        self.updated_at = self.aprovada_em

    def recusar_orcamento(self, referencia_externa: str | None = None) -> None:
        novo = transicao_apos_recusa(self.status)
        self.recusada_em = datetime.now(timezone.utc)
        if referencia_externa:
            self.referencia_externa = referencia_externa
        self._anexar_datas_se_aplicavel(novo)
        self.status = novo
        self.updated_at = self.recusada_em

    def _anexar_datas_se_aplicavel(self, destino: OrdemServicoStatus) -> None:
        now = datetime.now(timezone.utc)
        if destino == OrdemServicoStatus.FINALIZADA and self.data_finalizacao is None:
            self.data_finalizacao = now
        if destino == OrdemServicoStatus.ENTREGUE and self.data_entrega is None:
            self.data_entrega = now
