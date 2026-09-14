"""
Testes de INTEGRAÇÃO das rotas de /produto.

"Integração" aqui quer dizer: a gente usa o `client` (que simula a API
rodando de verdade) e chama as rotas HTTP, como um front-end faria.
Isso testa a rota + autenticação + service + repository + banco, tudo
junto -- diferente do teste unitário, que testava só o service isolado.
"""
from tests.helpers import criar_categoria, criar_funcionario


def login_e_pegar_header(client, funcionario, senha="senha123"):
    """Loga de verdade via POST /auth/login e devolve o header já pronto
    pra usar em outras chamadas (`headers=...`)."""
    resposta = client.post(
        "/auth/login",
        json={"login": funcionario.login, "password": senha, "type": "funcionario"},
    )
    token = resposta.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_listar_produtos_nao_precisa_de_login(client):
    resposta = client.get("/produto/list")

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_criar_produto_como_funcionario_logado(client, db_session):
    funcionario = criar_funcionario(db_session)
    categoria = criar_categoria(db_session)
    headers = login_e_pegar_header(client, funcionario)

    resposta = client.post(
        "/produto/internal",
        json={
            "nome": "Bolo de Cenoura",
            "preco": 30.0,
            "quantidade_estoque": 5,
            "id_categoria": str(categoria.id_categoria),
            "imagem_url": "https://example.com/bolo.jpg"
        },
        headers=headers,
    )

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Bolo de Cenoura"

    # Confirma que o produto criado pela rota realmente aparece na listagem.
    listagem = client.get("/produto/list")
    assert len(listagem.json()) == 1


def test_criar_produto_com_token_invalido_e_rejeitado(client, db_session):
    categoria = criar_categoria(db_session)

    resposta = client.post(
        "/produto/internal",
        json={
            "nome": "Bolo de Cenoura",
            "preco": 30.0,
            "quantidade_estoque": 5,
            "id_categoria": str(categoria.id_categoria),
             "imagem_url": "https://example.com/bolo.jpg"
        },
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert resposta.status_code == 401


def test_deletar_produto_como_funcionario(client, db_session):
    funcionario = criar_funcionario(db_session)
    categoria = criar_categoria(db_session)
    headers = login_e_pegar_header(client, funcionario)
    produto_criado = client.post(
        "/produto/internal",
        json={
            "nome": "Bolo de Cenoura",
            "preco": 30.0,
            "quantidade_estoque": 5,
            "id_categoria": str(categoria.id_categoria),
             "imagem_url": "https://example.com/bolo.jpg"
        },
        headers=headers,
    ).json()

    resposta = client.delete(f"/produto/internal/{produto_criado['id_produto']}", headers=headers)

    assert resposta.status_code == 200
    # Produto com soft delete não aparece mais na listagem pública.
    listagem = client.get("/produto/list")
    assert listagem.json() == []
