from tests.helpers import criar_cliente

def login_e_pegar_header(client, cliente, senha="123"):
    """Loga de verdade via POST /auth/login e devolve o header já pronto
    pra usar em outras chamadas (`headers=...`)."""
    resposta = client.post(
        "/auth/login",
        json={"login": cliente.login, "password": senha, "type": "cliente"},
    )
    if resposta.status_code == 200:
        token = resposta.json()["token"]
        return {"Authorization": f"Bearer {token}"}
    return None

def test_cliente_login(client, db_session):
    cliente = criar_cliente(db_session=db_session)
    assert login_e_pegar_header(client=client, cliente=cliente) is not None

def test_cliente_login_invalido(client, db_session):
    cliente = criar_cliente(db_session=db_session)
    assert login_e_pegar_header(client=client, cliente=cliente, senha="senha_invalida") is None
    