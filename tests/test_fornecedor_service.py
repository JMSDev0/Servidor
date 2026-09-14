"""
Testes UNITÁRIOS do FornecedorService: chama o service direto em Python.
"""
import pytest

from app.enums.tipo_funcionario import TipoFuncionario
from app.exceptions.exceptions import UnauthorizedException
from app.schemas.fornecedor.fornecedor_create import FornecedorCreate
from app.service.fornecedor_service import FornecedorService
from tests.helpers import criar_funcionario, usuario_logado

fornecedor_service = FornecedorService()


def dados_validos(cnpj: str = "11222333000181"):
    return FornecedorCreate(nome="Fornecedor LTDA", cnpj=cnpj, telefone="31999999999", email="fornecedor@teste.com")


def test_criar_fornecedor_como_gestor_funciona(db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)

    fornecedor = fornecedor_service.save(dados_validos(), usuario_logado(funcionario))

    assert fornecedor.nome == "Fornecedor LTDA"
    assert fornecedor.cnpj == "11222333000181"


def test_criar_fornecedor_como_vendedor_falha(db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.VENDEDOR)

    with pytest.raises(UnauthorizedException):
        fornecedor_service.save(dados_validos(), usuario_logado(funcionario))


def test_criar_fornecedor_com_cnpj_invalido_falha(db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)

    with pytest.raises(ValueError):
        fornecedor_service.save(dados_validos(cnpj="12345678900000"), usuario_logado(funcionario))


def test_criar_fornecedor_com_cnpj_duplicado_falha(db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)
    fornecedor_service.save(dados_validos(), usuario_logado(funcionario))

    with pytest.raises(ValueError):
        fornecedor_service.save(dados_validos(), usuario_logado(funcionario))


def test_find_retorna_fornecedor_criado(db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)
    fornecedor_service.save(dados_validos(), usuario_logado(funcionario))

    pagina = fornecedor_service.find(0, 20)

    assert pagina.total_items == 1
    assert pagina.content[0].cnpj == "11222333000181"


def test_get_by_id_retorna_fornecedor(db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)
    criado = fornecedor_service.save(dados_validos(), usuario_logado(funcionario))

    encontrado = fornecedor_service.get_by_id(criado.id_fornecedor)

    assert encontrado.nome == "Fornecedor LTDA"
