"""
Testes de INTEGRAÇÃO das rotas de /empresa-contrato: rota + autenticação +
service + repository + banco, chamando via `client` (como um front-end faria).
"""
from app.enums.tipo_funcionario import TipoFuncionario
from tests.helpers import CNPJ_VALIDO_1, criar_empresa_contrato, criar_funcionario


def login_e_pegar_header(client, funcionario, senha="senha123"):
    resposta = client.post(
        "/auth/login",
        json={"login": funcionario.login, "password": senha, "type": "funcionario"},
    )
    token = resposta.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_criar_empresa_contrato_como_gestor(client, db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)
    headers = login_e_pegar_header(client, funcionario)

    resposta = client.post(
        "/empresa-contrato",
        json={
            "nome": "Móveis Parceiro LTDA",
            "cnpj": CNPJ_VALIDO_1,
            "data_inicio": "2025-01-01",
        },
        headers=headers,
    )

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Móveis Parceiro LTDA"
    assert resposta.json()["contrato_ativo"] is True


def test_criar_empresa_contrato_como_vendedor_e_rejeitado(client, db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.VENDEDOR)
    headers = login_e_pegar_header(client, funcionario)

    resposta = client.post(
        "/empresa-contrato",
        json={"nome": "Móveis Parceiro LTDA", "cnpj": CNPJ_VALIDO_1, "data_inicio": "2025-01-01"},
        headers=headers,
    )

    assert resposta.status_code == 401


def test_criar_empresa_contrato_com_token_invalido_e_rejeitado(client):
    resposta = client.post(
        "/empresa-contrato",
        json={"nome": "Móveis Parceiro LTDA", "cnpj": CNPJ_VALIDO_1, "data_inicio": "2025-01-01"},
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert resposta.status_code == 401


def test_listar_empresas_contrato(client, db_session):
    criar_empresa_contrato(db_session)
    funcionario = criar_funcionario(db_session)
    headers = login_e_pegar_header(client, funcionario)

    resposta = client.get("/empresa-contrato/find", headers=headers)

    assert resposta.status_code == 200
    assert resposta.json()["total_items"] == 1


def test_atualizar_empresa_contrato_encerra_contrato(client, db_session):
    empresa = criar_empresa_contrato(db_session)
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)
    headers = login_e_pegar_header(client, funcionario)

    resposta = client.put(
        f"/empresa-contrato/{empresa.id_empresa_contrato}",
        json={"contrato_ativo": False},
        headers=headers,
    )

    assert resposta.status_code == 200
    assert resposta.json()["contrato_ativo"] is False


def test_buscar_empresa_contrato_inexistente_retorna_404(client, db_session):
    import uuid

    funcionario = criar_funcionario(db_session)
    headers = login_e_pegar_header(client, funcionario)

    resposta = client.get(f"/empresa-contrato/{uuid.uuid4()}", headers=headers)

    assert resposta.status_code == 404
