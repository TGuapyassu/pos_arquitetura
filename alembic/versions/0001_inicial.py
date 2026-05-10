"""Cria tabelas iniciais (PostgreSQL).

Revision ID: 0001
Revises:
Create Date: 2026-04-26
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "clientes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cpf_cnpj", sa.String(20), nullable=False),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("contato", sa.String(120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_clientes_cpf_cnpj", "clientes", ["cpf_cnpj"], unique=True)

    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(120), nullable=False),
        sa.Column("senha_hash", sa.String(255), nullable=False),
        sa.Column("is_admin", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=True)

    op.create_table(
        "servicos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("preco", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_servicos_nome", "servicos", ["nome"], unique=True)

    op.create_table(
        "pecas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("preco", sa.Numeric(12, 2), nullable=False),
        sa.Column("quantidade_estoque", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "veiculos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cliente_id", sa.Integer(), sa.ForeignKey("clientes.id"), nullable=False),
        sa.Column("placa", sa.String(10), nullable=False),
        sa.Column("marca", sa.String(80), nullable=False),
        sa.Column("modelo", sa.String(80), nullable=False),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_veiculos_cliente_id", "veiculos", ["cliente_id"])
    op.create_index("ix_veiculos_placa", "veiculos", ["placa"], unique=True)

    # Mesmo padrão do ORM: enum Python persistido em VARCHAR
    op.create_table(
        "ordens_servico",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cliente_id", sa.Integer(), sa.ForeignKey("clientes.id"), nullable=False),
        sa.Column("veiculo_id", sa.Integer(), sa.ForeignKey("veiculos.id"), nullable=False),
        sa.Column("status", sa.String(32), server_default=sa.text("'RECEBIDA'"), nullable=False),
        sa.Column("valor_total", sa.Numeric(12, 2), nullable=True),
        sa.Column("aprovada_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("data_finalizacao", sa.DateTime(timezone=True), nullable=True),
        sa.Column("data_entrega", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ordens_servico_cliente", "ordens_servico", ["cliente_id"])
    op.create_index("ix_ordens_servico_veiculo", "ordens_servico", ["veiculo_id"])

    op.create_table(
        "ordem_servico_itens_servico",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ordem_id", sa.Integer(), sa.ForeignKey("ordens_servico.id", ondelete="CASCADE")),
        sa.Column("servico_id", sa.Integer(), sa.ForeignKey("servicos.id"), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.Column("preco_unitario", sa.Numeric(12, 2), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ossv_ordem", "ordem_servico_itens_servico", ["ordem_id"])
    op.create_table(
        "ordem_servico_itens_peca",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ordem_id", sa.Integer(), sa.ForeignKey("ordens_servico.id", ondelete="CASCADE")),
        sa.Column("peca_id", sa.Integer(), sa.ForeignKey("pecas.id"), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.Column("preco_unitario", sa.Numeric(12, 2), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_osp_peca", "ordem_servico_itens_peca", ["ordem_id"])


def downgrade() -> None:
    op.drop_index("ix_osp_peca", table_name="ordem_servico_itens_peca")
    op.drop_table("ordem_servico_itens_peca")
    op.drop_index("ix_ossv_ordem", table_name="ordem_servico_itens_servico")
    op.drop_table("ordem_servico_itens_servico")
    op.drop_index("ix_ordens_servico_veiculo", table_name="ordens_servico")
    op.drop_index("ix_ordens_servico_cliente", table_name="ordens_servico")
    op.drop_table("ordens_servico")
    op.drop_index("ix_veiculos_placa", table_name="veiculos")
    op.drop_index("ix_veiculos_cliente_id", table_name="veiculos")
    op.drop_table("veiculos")
    op.drop_table("pecas")
    op.drop_index("ix_servicos_nome", table_name="servicos")
    op.drop_table("servicos")
    op.drop_index("ix_usuarios_email", table_name="usuarios")
    op.drop_table("usuarios")
    op.drop_index("ix_clientes_cpf_cnpj", table_name="clientes")
    op.drop_table("clientes")
