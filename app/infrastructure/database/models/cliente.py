from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base import Base


class ClienteOrm(Base):
    __tablename__ = "clientes"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cpf_cnpj: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    contato: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    veiculos: Mapped[List["VeiculoOrm"]] = relationship(back_populates="cliente")
