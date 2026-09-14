"""
Testes UNITÁRIOS do FuncionarioService: chama o service direto em Python.
"""
from datetime import date

import pytest

from app.enums.tipo_funcionario import TipoFuncionario
from app.exceptions.exceptions import UnauthorizedException
from app.schemas.funcionario.funcionario_create import FuncionarioCreate
from app.service.funcionario_service import FuncionarioService
from tests.helpers import criar_funcionario, usuario_logado

funcionario_service = FuncionarioService()


def dados_validos(
    cpf="01474777198",
    email="novo@teste.com",
    login="novo_login",
    tipo=TipoFuncionario.VENDEDOR,
    comissao=5.0,
):
    return FuncionarioCreate(
        nome="Novo Funcionario",
        cpf=cpf,
        email=email,
        senha="senha123",
        login=login,
        telefone="31988888888",
        endereco="Rua Nova, 1",
        data_nascimento=date(1990, 1, 1),
        salario=2000.0,
        tipo=tipo,
        comissao_percentual=comissao,
    )


def test_gestor_cria_vendedor_com_sucesso(db_session):
    ator = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)

    criado = funcionario_service.save(dados_validos(), usuario_logado(ator))

    assert criado.login == "novo_login"
    assert criado.tipo == "vendedor"
    assert criado.comissao_percentual == 5.0


def test_vendedor_nao_pode_cadastrar_funcionario(db_session):
    ator = criar_funcionario(db_session, tipo=TipoFuncionario.VENDEDOR)

    with pytest.raises(UnauthorizedException):
        funcionario_service.save(dados_validos(), usuario_logado(ator))


def test_gestor_nao_pode_cadastrar_administrador(db_session):
    """RN-FUN-02: gestor só administra cadastro de estoquista/vendedor."""
    ator = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)

    with pytest.raises(UnauthorizedException):
        funcionario_service.save(
            dados_validos(tipo=TipoFuncionario.ADMIN, comissao=0.0), usuario_logado(ator)
        )


def test_cpf_duplicado_falha(db_session):
    """`ator` (GESTOR) já ocupa o cpf padrão de `criar_funcionario` -- reusa como duplicado."""
    ator = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)

    with pytest.raises(ValueError):
        funcionario_service.save(dados_validos(cpf=ator.cpf), usuario_logado(ator))


def test_email_duplicado_falha(db_session):
    ator = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)

    with pytest.raises(ValueError):
        funcionario_service.save(dados_validos(email=ator.email), usuario_logado(ator))


def test_login_duplicado_falha(db_session):
    ator = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)

    with pytest.raises(ValueError):
        funcionario_service.save(dados_validos(login=ator.login), usuario_logado(ator))


def test_comissao_percentual_para_nao_vendedor_falha(db_session):
    """RN-FUN-03: comissao_percentual só é válido para tipo=vendedor."""
    ator = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)

    with pytest.raises(ValueError):
        funcionario_service.save(
            dados_validos(tipo=TipoFuncionario.ESTOQUISTA, comissao=10.0), usuario_logado(ator)
        )


def test_soft_delete_desativa_funcionario(db_session):
    """RN-FUN-04: exclusão é soft delete (ativo=False), não remoção física."""
    ator = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)
    criado = funcionario_service.save(dados_validos(), usuario_logado(ator))

    funcionario_service.soft_delete(criado.id_funcionario, usuario_logado(ator))

    # criado.id_funcionario já é um UUID (não uma string) -- passar direto.
    funcionario_no_banco = funcionario_service.get_by_id(criado.id_funcionario)
    assert funcionario_no_banco is not None
    assert funcionario_no_banco.ativo is False
