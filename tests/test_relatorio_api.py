"""
Testes de INTEGRAÇÃO da rota /relatorio/margem.
"""
from app.enums.tipo_funcionario import TipoFuncionario
from tests.helpers import criar_funcionario, criar_produto


def login_e_pegar_header(client, funcionario, senha="senha123"):
    resposta = client.post(
        "/auth/login",
        json={"login": funcionario.login, "password": senha, "type": "funcionario"},
    )
    token = resposta.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_relatorio_margem_como_gestor(client, db_session):
    criar_produto(db_session, preco=100.0, custo=60.0)
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.GESTOR)
    headers = login_e_pegar_header(client, funcionario)

    resposta = client.get("/relatorio/margem", headers=headers)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert len(corpo) == 1
    assert corpo[0]["margem_percentual"] == 40.0


def test_relatorio_margem_como_estoquista_e_rejeitado(client, db_session):
    funcionario = criar_funcionario(db_session, tipo=TipoFuncionario.ESTOQUISTA)
    headers = login_e_pegar_header(client, funcionario)

    resposta = client.get("/relatorio/margem", headers=headers)

    assert resposta.status_code == 401


def test_relatorio_margem_com_token_invalido_e_rejeitado(client):
    resposta = client.get("/relatorio/margem", headers={"Authorization": "Bearer token-invalido"})

    assert resposta.status_code == 401
