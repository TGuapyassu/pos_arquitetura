from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)

# native_enum=False: compatível com SQLite (testes) e com PostgreSQL (VARCHAR).
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import OrdemServicoStatus
from app.infrastructure.database.models.base import Base

_status_enum = SAEnum(
    OrdemServicoStatus,
    name="ordem_servico_status",
    native_enum=False,
    values_callable=lambda x: [e.value for e in x],
)


class OrdemServicoOrm(Base):
    __tablename__ = "ordens_servico"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), index=True)
    veiculo_id: Mapped[int] = mapped_column(ForeignKey("veiculos.id"), index=True)
    status: Mapped[OrdemServicoStatus] = mapped_column(
        _status_enum,
        default=OrdemServicoStatus.RECEBIDA,
    )
    valor_total: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    aprovada_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recusada_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    referencia_externa: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    data_finalizacao: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    data_entrega: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    itens_servico: Mapped[List["OrdemServicoServicoOrm"]] = relationship(
        back_populates="os", cascade="all, delete-orphan"
    )
    itens_peca: Mapped[List["OrdemServicoPecaOrm"]] = relationship(
        back_populates="os", cascade="all, delete-orphan"
    )


class OrdemServicoServicoOrm(Base):
    __tablename__ = "ordem_servico_itens_servico"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ordem_id: Mapped[int] = mapped_column(
        ForeignKey("ordens_servico.id", ondelete="CASCADE"), index=True
    )
    servico_id: Mapped[int] = mapped_column(ForeignKey("servicos.id"))
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    os: Mapped[OrdemServicoOrm] = relationship(back_populates="itens_servico")


class OrdemServicoPecaOrm(Base):
    __tablename__ = "ordem_servico_itens_peca"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ordem_id: Mapped[int] = mapped_column(
        ForeignKey("ordens_servico.id", ondelete="CASCADE"), index=True
    )
    peca_id: Mapped[int] = mapped_column(ForeignKey("pecas.id"))
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    os: Mapped[OrdemServicoOrm] = relationship(back_populates="itens_peca")
