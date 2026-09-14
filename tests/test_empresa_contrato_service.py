"""
Testes UNITÁRIOS do EmpresaContratoService: chamam o service direto em
Python, sem passar por HTTP. Foco em regra de negócio (validação, permissão).
"""
import uuid
from datetime import date

import pytest

from app.enums.tipo_funcionario import TipoFuncionario
from app.exceptions.exceptions import EntityNotFoundException, UnauthorizedException
from app.schemas.empresa.empresa_contrato_create import EmpresaContratoCreate
from app.schemas.empresa.empresa_contrato_update import EmpresaContratoUpdate
from app.service.empresa_contrato_service import EmpresaContratoService
from tests.helpers import CNPJ_VALIDO_1, criar_empresa_contrato, criar_funcionario, usuario_logado

empresa_contrato_service = EmpresaContratoService()


def dados_validos(cnpj: str = CNPJ_VALIDO_1):
    return EmpresaContratoCreate(
        nome="Móveis Parceiro LTDA",
        cnpj=cnpj,
        data_inicio=date(2025, 1, 1),
    )


def test_criar_empresa_contrato_como_gestor_funciona(db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)

    empresa = empresa_contrato_service.save(dados_validos(), usuario_logado(funcionario))

    assert empresa.nome == "Móveis Parceiro LTDA"
    assert empresa.cnpj == CNPJ_VALIDO_1
    assert empresa.contrato_ativo is True


def test_criar_empresa_contrato_como_vendedor_falha(db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.VENDEDOR)

    with pytest.raises(UnauthorizedException):
        empresa_contrato_service.save(dados_validos(), usuario_logado(funcionario))


def test_criar_empresa_contrato_como_administrador_funciona(db_session):
    """ADMIN sempre passa em check_user_permission, mesmo fora de required_roles."""
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.ADMIN)

    empresa = empresa_contrato_service.save(dados_validos(), usuario_logado(funcionario))

    assert empresa.cnpj == CNPJ_VALIDO_1


def test_criar_empresa_contrato_com_cnpj_invalido_falha(db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)
    dados = dados_validos(cnpj="12345678900000")

    with pytest.raises(ValueError):
        empresa_contrato_service.save(dados, usuario_logado(funcionario))


def test_criar_empresa_contrato_com_cnpj_duplicado_falha(db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)
    criar_empresa_contrato(db_session, cnpj=CNPJ_VALIDO_1)

    with pytest.raises(ValueError):
        empresa_contrato_service.save(dados_validos(cnpj=CNPJ_VALIDO_1), usuario_logado(funcionario))


def test_criar_empresa_contrato_com_data_fim_antes_de_inicio_falha(db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)
    dados = EmpresaContratoCreate(
        nome="Móveis Parceiro LTDA",
        cnpj=CNPJ_VALIDO_1,
        data_inicio=date(2025, 6, 1),
        data_fim=date(2025, 1, 1),
    )

    with pytest.raises(ValueError):
        empresa_contrato_service.save(dados, usuario_logado(funcionario))


def test_buscar_empresa_contrato_que_nao_existe_falha(db_session):
    funcionario = criar_funcionario(db_session)

    with pytest.raises(EntityNotFoundException):
        empresa_contrato_service.get_by_id(uuid.uuid4(), usuario_logado(funcionario))


def test_qualquer_funcionario_pode_consultar_empresa_contrato(db_session):
    """Leitura (get_by_id/find) não exige cargo gestor -- só estar logado."""
    empresa = criar_empresa_contrato(db_session)
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.ESTOQUISTA)

    encontrada = empresa_contrato_service.get_by_id(empresa.id_empresa_contrato, usuario_logado(funcionario))

    assert encontrada.id_empresa_contrato == empresa.id_empresa_contrato


def test_renovar_contrato_atualiza_data_fim_e_reativa(db_session):
    """RF019 (renovação): estende data_fim e reativa contrato_ativo."""
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)
    empresa = criar_empresa_contrato(db_session, contrato_ativo=False)

    atualizado = empresa_contrato_service.update(
        empresa.id_empresa_contrato,
        EmpresaContratoUpdate(data_fim=date(2026, 12, 31), contrato_ativo=True),
        usuario_logado(funcionario),
    )

    assert atualizado.data_fim == date(2026, 12, 31)
    assert atualizado.contrato_ativo is True


def test_atualizar_empresa_contrato_como_vendedor_falha(db_session):
    empresa = criar_empresa_contrato(db_session)
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.VENDEDOR)

    with pytest.raises(UnauthorizedException):
        empresa_contrato_service.update(
            empresa.id_empresa_contrato,
            EmpresaContratoUpdate(contrato_ativo=False),
            usuario_logado(funcionario),
        )
