"""add aguardando_precificacao status

Revision ID: ad81a1df2ee4
Revises: 9088a2101975
Create Date: 2026-08-12 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'ad81a1df2ee4'
down_revision: Union[str, Sequence[str], None] = '9088a2101975'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE orcamentostatus ADD VALUE IF NOT EXISTS 'AGUARDANDO_PRECIFICACAO'")


def downgrade() -> None:
    pass
