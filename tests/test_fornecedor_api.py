"""
Testes de INTEGRAÇÃO das rotas de /fornecedor.
"""
from app.enums.tipo_funcionario import TipoFuncionario
from tests.helpers import criar_funcionario


def login_e_pegar_header(client, funcionario, senha="senha123"):
    resposta = client.post(
        "/auth/login",
        json={"login": funcionario.login, "password": senha, "type": "funcionario"},
    )
    token = resposta.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_criar_fornecedor_como_gestor(client, db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)
    headers = login_e_pegar_header(client, funcionario)

    resposta = client.post(
        "/fornecedor",
        json={"nome": "Fornecedor LTDA", "cnpj": "11222333000181"},
        headers=headers,
    )

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Fornecedor LTDA"


def test_criar_fornecedor_como_vendedor_e_rejeitado(client, db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.VENDEDOR)
    headers = login_e_pegar_header(client, funcionario)

    resposta = client.post(
        "/fornecedor",
        json={"nome": "Fornecedor LTDA", "cnpj": "11222333000181"},
        headers=headers,
    )

    assert resposta.status_code == 401


def test_listar_fornecedores(client, db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)
    headers = login_e_pegar_header(client, funcionario)
    client.post("/fornecedor", json={"nome": "Fornecedor LTDA", "cnpj": "11222333000181"}, headers=headers)

    resposta = client.get("/fornecedor/find", headers=headers)

    assert resposta.status_code == 200
    assert resposta.json()["total_items"] == 1
