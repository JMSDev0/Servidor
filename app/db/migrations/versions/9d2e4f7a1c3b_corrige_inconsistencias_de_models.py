"""corrige inconsistencias de models (unique cliente, item_carrinho, produto.id_categoria, nomes de coluna)

Revision ID: 9d2e4f7a1c3b
Revises: 84a7ec39fc4c
Create Date: 2026-08-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d2e4f7a1c3b'
down_revision: Union[str, Sequence[str], None] = '84a7ec39fc4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # cliente: cpf/email/login precisam ser unicos (RN-CLI-01), igual ja e feito em funcionario
    op.create_unique_constraint('cliente_cpf_key', 'cliente', ['cpf'])
    op.create_unique_constraint('cliente_email_key', 'cliente', ['email'])
    op.create_unique_constraint('cliente_login_key', 'cliente', ['login'])

    # item_carrinho: unique tinha sido criado por coluna (impedia mais de 1 item por carrinho
    # e o mesmo produto em mais de um carrinho no sistema todo); o correto e a combinacao das duas
    op.drop_constraint('item_carrinho_id_carrinho_key', 'item_carrinho', type_='unique')
    op.drop_constraint('item_carrinho_id_produto_key', 'item_carrinho', type_='unique')
    op.create_unique_constraint('uq_item_carrinho_carrinho_produto', 'item_carrinho', ['id_carrinho', 'id_produto'])

    # produto.id_categoria precisa aceitar NULL com ON DELETE SET NULL (RN-CAT-01: excluir
    # categoria nao pode apagar o produto, so deixa ele sem categoria)
    op.drop_constraint('produto_id_categoria_fkey', 'produto', type_='foreignkey')
    op.alter_column('produto', 'id_categoria', existing_type=sa.UUID(), nullable=True)
    op.create_foreign_key('produto_id_categoria_fkey', 'produto', 'categoria', ['id_categoria'], ['id_categoria'], ondelete='SET NULL')

    # nomes de coluna que nao batiam com a DDL/documentacao de requisitos
    op.alter_column('orcamento', 'data_validado', new_column_name='data_validade')
    op.alter_column('empresa_contrato', 'info_contato', new_column_name='info_contrato')


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('empresa_contrato', 'info_contrato', new_column_name='info_contato')
    op.alter_column('orcamento', 'data_validade', new_column_name='data_validado')

    op.drop_constraint('produto_id_categoria_fkey', 'produto', type_='foreignkey')
    op.alter_column('produto', 'id_categoria', existing_type=sa.UUID(), nullable=False)
    op.create_foreign_key('produto_id_categoria_fkey', 'produto', 'categoria', ['id_categoria'], ['id_categoria'])

    op.drop_constraint('uq_item_carrinho_carrinho_produto', 'item_carrinho', type_='unique')
    op.create_unique_constraint('item_carrinho_id_produto_key', 'item_carrinho', ['id_produto'])
    op.create_unique_constraint('item_carrinho_id_carrinho_key', 'item_carrinho', ['id_carrinho'])

    op.drop_constraint('cliente_login_key', 'cliente', type_='unique')
    op.drop_constraint('cliente_email_key', 'cliente', type_='unique')
    op.drop_constraint('cliente_cpf_key', 'cliente', type_='unique')
