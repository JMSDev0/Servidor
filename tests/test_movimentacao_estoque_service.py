"""
Testes UNITÁRIOS de movimentação de estoque (ProdutoService.register_stock_movement
/ get_stock_movements) -- RN-MOV-01/02/03. Não existe um "MovimentacaoEstoqueService"
separado, essa lógica vive dentro de ProdutoService.
"""
import pytest

from app.enums.tipo_movimentacao import TipoMovimentacao
from app.schemas.movimentacao_estoque import MovimentacaoEstoqueCreate
from app.service.produto_service import ProdutoService
from tests.helpers import criar_produto

produto_service = ProdutoService()


def test_entrada_aumenta_quantidade_estoque(db_session):
    produto = criar_produto(db_session, quantidade_estoque=10)

    produto_service.register_stock_movement(MovimentacaoEstoqueCreate(
        id_produto=produto.id_produto,
        quantidade=5,
        tipo_movimentacao=TipoMovimentacao.ENTRADA,
    ))

    atualizado = produto_service.get_by_id(produto.id_produto)
    assert atualizado.quantidade_estoque == 15


def test_saida_diminui_quantidade_estoque(db_session):
    produto = criar_produto(db_session, quantidade_estoque=10)

    produto_service.register_stock_movement(MovimentacaoEstoqueCreate(
        id_produto=produto.id_produto,
        quantidade=4,
        tipo_movimentacao=TipoMovimentacao.SAIDA,
    ))

    atualizado = produto_service.get_by_id(produto.id_produto)
    assert atualizado.quantidade_estoque == 6


def test_saida_maior_que_estoque_falha(db_session):
    produto = criar_produto(db_session, quantidade_estoque=3)

    with pytest.raises(ValueError):
        produto_service.register_stock_movement(MovimentacaoEstoqueCreate(
            id_produto=produto.id_produto,
            quantidade=10,
            tipo_movimentacao=TipoMovimentacao.SAIDA,
        ))

    # Falhou antes de commitar a baixa -- estoque não deve ter mudado.
    atualizado = produto_service.get_by_id(produto.id_produto)
    assert atualizado.quantidade_estoque == 3


def test_historico_de_movimentacao_por_produto(db_session):
    produto = criar_produto(db_session, quantidade_estoque=10)
    produto_service.register_stock_movement(MovimentacaoEstoqueCreate(
        id_produto=produto.id_produto, quantidade=5, tipo_movimentacao=TipoMovimentacao.ENTRADA,
    ))
    produto_service.register_stock_movement(MovimentacaoEstoqueCreate(
        id_produto=produto.id_produto, quantidade=2, tipo_movimentacao=TipoMovimentacao.SAIDA,
    ))

    historico = produto_service.get_stock_movements(produto.id_produto)

    assert len(historico) == 2
