"""
Testes de INTEGRAÇÃO das rotas de /produto/internal/movimentacao.
"""
from tests.helpers import criar_funcionario, criar_produto


def login_e_pegar_header(client, funcionario, senha="senha123"):
    resposta = client.post(
        "/auth/login",
        json={"login": funcionario.login, "password": senha, "type": "funcionario"},
    )
    token = resposta.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_registrar_entrada_de_estoque(client, db_session):
    produto = criar_produto(db_session, quantidade_estoque=10)
    funcionario = criar_funcionario(db_session)
    headers = login_e_pegar_header(client, funcionario)

    resposta = client.post(
        "/produto/internal/movimentacao",
        json={
            "id_produto": str(produto.id_produto),
            "quantidade": 5,
            "tipo_movimentacao": "entrada",
        },
        headers=headers,
    )

    assert resposta.status_code == 200

    historico = client.get(f"/produto/internal/movimentacao/{produto.id_produto}", headers=headers)
    assert len(historico.json()) == 1


def test_registrar_movimentacao_sem_token_e_rejeitado(client, db_session):
    produto = criar_produto(db_session, quantidade_estoque=10)

    resposta = client.post(
        "/produto/internal/movimentacao",
        json={"id_produto": str(produto.id_produto), "quantidade": 5, "tipo_movimentacao": "entrada"},
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert resposta.status_code == 401
