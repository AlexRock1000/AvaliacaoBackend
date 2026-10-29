"""Ativa RLS nas tabelas do projeto para bloquear a Data API sem políticas.

Revision ID: 0002_ativar_rls
Revises: 0001_esquema_inicial
Create Date: 2026-10-29
"""

from alembic import op


revision = "0002_ativar_rls"
down_revision = "0001_esquema_inicial"
branch_labels = None
depends_on = None


TABELAS = (
    "grupos",
    "permissoes",
    "grupo_permissoes",
    "usuarios",
    "usuario_grupos",
    "tatuagens",
    "passos",
    "alembic_version",
)


def upgrade():
    for tabela in TABELAS:
        op.execute(f"ALTER TABLE {tabela} ENABLE ROW LEVEL SECURITY")


def downgrade():
    for tabela in TABELAS:
        op.execute(f"ALTER TABLE {tabela} DISABLE ROW LEVEL SECURITY")
