"""Baseline para o esquema criado por criar_tabelas.py.

Revision ID: 0001_esquema_inicial
Revises:
Create Date: 2026-10-28
"""

revision = "0001_esquema_inicial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """O esquema inicial é criado pelo script criar_tabelas.py."""


def downgrade():
    """O baseline não remove dados nem tabelas."""
