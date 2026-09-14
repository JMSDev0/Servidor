"""
Testes de INTEGRAÇÃO das rotas de /orcamento/internal.
"""
from tests.helpers import criar_cliente, criar_funcionario, criar_produto


def login_e_pegar_header(client, funcionario, senha="senha123"):
    resposta = client.post(
        "/auth/login",
        json={"login": funcionario.login, "password": senha, "type": "funcionario"},
    )
    token = resposta.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_criar_orcamento_via_api(client, db_session):
    funcionario = criar_funcionario(db_session)
    cliente = criar_cliente(db_session)
    produto = criar_produto(db_session, preco=25.0)
    headers = login_e_pegar_header(client, funcionario)

    resposta = client.post(
        "/orcamento/internal",
        json={
            "id_cliente": str(cliente.id_cliente),
            "itens": [{"id_produto": str(produto.id_produto), "quantidade": 4}],
        },
        headers=headers,
    )

    assert resposta.status_code == 200
    assert resposta.json()["valor_total"] == 100.0
    assert resposta.json()["status"] == "pendente"


def test_criar_orcamento_com_token_invalido_e_rejeitado(client, db_session):
    produto = criar_produto(db_session)

    resposta = client.post(
        "/orcamento/internal",
        json={"itens": [{"id_produto": str(produto.id_produto), "quantidade": 1}]},
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert resposta.status_code == 401


def test_aprovar_orcamento_via_api_gera_pedido(client, db_session):
    funcionario = criar_funcionario(db_session)
    cliente = criar_cliente(db_session)
    produto = criar_produto(db_session, preco=25.0)
    headers = login_e_pegar_header(client, funcionario)

    criado = client.post(
        "/orcamento/internal",
        json={
            "id_cliente": str(cliente.id_cliente),
            "itens": [{"id_produto": str(produto.id_produto), "quantidade": 2}],
        },
        headers=headers,
    ).json()

    resposta = client.patch(
        f"/orcamento/internal/status/{criado['id_orcamento']}?new_status=aprovado",
        json={"forma_pagamento": "pix", "endereco_entrega_texto": "Rua Teste, 123"},
        headers=headers,
    )

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "aprovado"


def test_listar_orcamentos(client, db_session):
    funcionario = criar_funcionario(db_session)
    cliente = criar_cliente(db_session)
    produto = criar_produto(db_session)
    headers = login_e_pegar_header(client, funcionario)
    client.post(
        "/orcamento/internal",
        json={
            "id_cliente": str(cliente.id_cliente),
            "itens": [{"id_produto": str(produto.id_produto), "quantidade": 1}],
        },
        headers=headers,
    )

    resposta = client.get("/orcamento/internal/find", headers=headers)

    assert resposta.status_code == 200
    assert resposta.json()["total_items"] == 1
