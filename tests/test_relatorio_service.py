"""
Testes UNITÁRIOS do RelatorioService (RF16 - margem de produtos).
"""
import pytest

from app.enums.tipo_funcionario import TipoFuncionario
from app.exceptions.exceptions import UnauthorizedException
from app.service.relatorio_service import RelatorioService
from tests.helpers import criar_funcionario, criar_produto, usuario_logado

relatorio_service = RelatorioService()


def test_margem_calculada_a_partir_do_custo_do_fornecedor(db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)
    criar_produto(db_session, preco=100.0, custo=60.0)

    itens = relatorio_service.margem_produtos(usuario_logado(funcionario))

    assert len(itens) == 1
    assert itens[0].preco_venda == 100.0
    assert itens[0].custo_medio == 60.0
    assert itens[0].margem_valor == 40.0
    assert itens[0].margem_percentual == 40.0


def test_produto_sem_fornecedor_aparece_sem_margem_calculavel(db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)
    criar_produto(db_session, preco=50.0)

    itens = relatorio_service.margem_produtos(usuario_logado(funcionario))

    assert len(itens) == 1
    assert itens[0].custo_medio is None
    assert itens[0].margem_percentual is None


def test_relatorio_ordena_menor_margem_primeiro(db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)
    criar_produto(db_session, preco=100.0, custo=90.0)  # margem 10%
    criar_produto(db_session, preco=100.0, custo=50.0)  # margem 50%

    itens = relatorio_service.margem_produtos(usuario_logado(funcionario))

    assert itens[0].margem_percentual == 10.0
    assert itens[1].margem_percentual == 50.0


def test_relatorio_como_vendedor_falha(db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.VENDEDOR)

    with pytest.raises(UnauthorizedException):
        relatorio_service.margem_produtos(usuario_logado(funcionario))
