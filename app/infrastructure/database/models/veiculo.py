from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base import Base


class VeiculoOrm(Base):
    __tablename__ = "veiculos"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), index=True)
    placa: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    marca: Mapped[str] = mapped_column(String(80), nullable=False)
    modelo: Mapped[str] = mapped_column(String(80), nullable=False)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    cliente: Mapped["ClienteOrm"] = relationship(back_populates="veiculos")
