"""
Testes de INTEGRAÇÃO das rotas de /funcionario.
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


def payload_novo_funcionario(**overrides):
    dados = {
        "nome": "Novo Funcionario",
        "cpf": "01474777198",
        "email": "novo@teste.com",
        "senha": "senha123",
        "login": "novo_login",
        "telefone": "31988888888",
        "endereco": "Rua Nova, 1",
        "data_nascimento": "1990-01-01",
        "salario": 2000.0,
        "tipo": "vendedor",
        "comissao_percentual": 5.0,
    }
    dados.update(overrides)
    return dados


def test_criar_funcionario_como_gestor(client, db_session):
    ator = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)
    headers = login_e_pegar_header(client, ator)

    resposta = client.post("/funcionario", json=payload_novo_funcionario(), headers=headers)

    assert resposta.status_code == 200
    assert resposta.json()["login"] == "novo_login"


def test_criar_funcionario_como_vendedor_e_rejeitado(client, db_session):
    ator = criar_funcionario(db_session, tipo=TipoFuncionario.VENDEDOR)
    headers = login_e_pegar_header(client, ator)

    resposta = client.post("/funcionario", json=payload_novo_funcionario(), headers=headers)

    assert resposta.status_code == 401


def test_desativar_funcionario_via_api(client, db_session):
    ator = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)
    headers = login_e_pegar_header(client, ator)
    criado = client.post("/funcionario", json=payload_novo_funcionario(), headers=headers).json()

    resposta = client.delete(f"/funcionario/{criado['id_funcionario']}", headers=headers)

    assert resposta.status_code == 200
