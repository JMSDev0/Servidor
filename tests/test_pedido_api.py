"""
Testes de INTEGRAÇÃO das rotas de /pedido/internal.
"""
from tests.helpers import criar_cliente, criar_funcionario, criar_produto


def login_e_pegar_header(client, funcionario, senha="senha123"):
    resposta = client.post(
        "/auth/login",
        json={"login": funcionario.login, "password": senha, "type": "funcionario"},
    )
    token = resposta.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_criar_e_buscar_pedido_via_api(client, db_session):
    funcionario = criar_funcionario(db_session)
    cliente = criar_cliente(db_session)
    produto = criar_produto(db_session, preco=20.0, quantidade_estoque=10)
    headers = login_e_pegar_header(client, funcionario)

    criado = client.post(
        "/pedido/internal",
        json={
            "forma_pagamento": "pix",
            "itens": [{"id_produto": str(produto.id_produto), "quantidade": 2}],
            "id_cliente": str(cliente.id_cliente),
            "endereco_entrega_texto": "Rua Teste, 123",
        },
        headers=headers,
    ).json()

    assert criado["valor_total"] == 40.0

    resposta = client.get(f"/pedido/internal/{criado['id_pedido']}", headers=headers)
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "pendente"


def test_criar_pedido_com_token_invalido_e_rejeitado(client, db_session):
    produto = criar_produto(db_session)

    resposta = client.post(
        "/pedido/internal",
        json={
            "forma_pagamento": "pix",
            "itens": [{"id_produto": str(produto.id_produto), "quantidade": 1}],
            "endereco_entrega_texto": "Rua Teste, 123",
        },
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert resposta.status_code == 401
