"""
Testes UNITÁRIOS do ProdutoService.

"Unitário" aqui quer dizer: a gente chama o método do service direto em
Python (`produto_service.save(...)`), sem passar por HTTP. O foco é
testar a regra de negócio (validação, permissão) isolada do resto.
"""
import uuid

import pytest

from app.exceptions.exceptions import EntityNotFoundException, UnauthorizedException
from app.schemas.produto.produto_create import ProdutoCreate
from app.service.produto_service import ProdutoService
from tests.helpers import criar_categoria, criar_funcionario, usuario_logado

produto_service = ProdutoService()


def test_criar_produto_com_dados_validos_funciona(db_session):
    funcionario = criar_funcionario(db_session)
    categoria = criar_categoria(db_session)
    dados = ProdutoCreate(
        nome="Bolo de Chocolate",
        preco=25.0,
        quantidade_estoque=10,
        id_categoria=categoria.id_categoria,
    )

    produto = produto_service.save(dados, usuario_logado(funcionario))

    assert produto.nome == "Bolo de Chocolate"
    assert produto.quantidade_estoque == 10
    assert produto.ativo is True


def test_criar_produto_sem_nome_falha(db_session):
    funcionario = criar_funcionario(db_session)
    categoria = criar_categoria(db_session)
    dados = ProdutoCreate(
        nome="",
        preco=25.0,
        quantidade_estoque=10,
        id_categoria=categoria.id_categoria,
        imagem_url="https://example.com/bolo.jpg"
    )

    # pytest.raises: diz "eu espero que o código dentro do `with` dê esse
    # erro". Se não der erro nenhum, o teste falha.
    with pytest.raises(ValueError):
        produto_service.save(dados, usuario_logado(funcionario))


def test_criar_produto_com_preco_negativo_falha(db_session):
    funcionario = criar_funcionario(db_session)
    categoria = criar_categoria(db_session)
    dados = ProdutoCreate(
        nome="Bolo de Chocolate",
        preco=-10,
        quantidade_estoque=10,
        id_categoria=categoria.id_categoria,
        imagem_url="https://example.com/bolo.jpg"
    )

    with pytest.raises(ValueError):
        produto_service.save(dados, usuario_logado(funcionario))


def test_criar_produto_sem_estar_logado_falha(db_session):
    categoria = criar_categoria(db_session)
    dados = ProdutoCreate(
        nome="Bolo de Chocolate",
        preco=25.0,
        quantidade_estoque=10,
        id_categoria=categoria.id_categoria,
        imagem_url="https://example.com/bolo.jpg"
    )

    # current_user=None simula quem não está logado (sem token).
    with pytest.raises(UnauthorizedException):
        produto_service.save(dados, current_user=None)


def test_deletar_produto_que_nao_existe_falha(db_session):
    funcionario = criar_funcionario(db_session)
    id_que_nao_existe = uuid.uuid4()

    with pytest.raises(EntityNotFoundException):
        produto_service.delete(id_que_nao_existe, usuario_logado(funcionario))


def test_deletar_produto_faz_soft_delete(db_session):
    """
    "Soft delete" = o produto não é removido do banco, só marcado como
    inativo (`ativo = False`). O teste confirma isso, e não que a linha
    desapareceu.
    """
    funcionario = criar_funcionario(db_session)
    categoria = criar_categoria(db_session)
    dados = ProdutoCreate(
        nome="Bolo de Chocolate",
        preco=25.0,
        quantidade_estoque=10,
        id_categoria=categoria.id_categoria,
        imagem_url="https://example.com/bolo.jpg"
    )
    produto = produto_service.save(dados, usuario_logado(funcionario))

    produto_service.delete(produto.id_produto, usuario_logado(funcionario))

    produto_no_banco = produto_service.get_by_id(produto.id_produto)
    assert produto_no_banco is not None
    assert produto_no_banco.ativo is False
