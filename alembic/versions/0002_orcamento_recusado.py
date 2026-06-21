"""Adiciona ORCAMENTO_RECUSADO e campos de recusa externa.

Revision ID: 0002
Revises: 0001
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ordens_servico",
        sa.Column("recusada_em", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "ordens_servico",
        sa.Column("referencia_externa", sa.String(255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("ordens_servico", "referencia_externa")
    op.drop_column("ordens_servico", "recusada_em")
