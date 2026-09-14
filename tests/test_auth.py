"""
Testes de login/autenticação.

Esse arquivo mistura os dois tipos de teste, pra dar pra comparar:
- UNITÁRIO: chama `authenticate()` direto (sem HTTP).
- INTEGRAÇÃO: chama a rota POST /auth/login de verdade, via `client`.
"""
from app.service.auth_service import authenticate
from tests.helpers import criar_funcionario


# ---------- Unitário ----------

def test_authenticate_com_senha_certa_devolve_token(db_session):
    funcionario = criar_funcionario(db_session)  # senha padrão: "senha123"

    resultado = authenticate(funcionario.login, "senha123", type="funcionario")

    assert resultado is not False
    token, payload = resultado
    assert isinstance(token, str)
    assert payload["login"] == funcionario.login


def test_authenticate_com_senha_errada_devolve_false(db_session):
    funcionario = criar_funcionario(db_session)

    resultado = authenticate(funcionario.login, "senha-errada", type="funcionario")

    assert resultado is False


def test_authenticate_com_login_que_nao_existe_devolve_false(db_session):
    resultado = authenticate("login_que_nao_existe", "qualquer-senha", type="funcionario")

    assert resultado is False


def test_authenticate_de_funcionario_inativo_devolve_false(db_session):
    funcionario = criar_funcionario(db_session)
    funcionario.ativo = False
    db_session.commit()

    resultado = authenticate(funcionario.login, "senha123", type="funcionario")

    assert resultado is False


# ---------- Integração ----------

def test_login_via_api_com_sucesso(client, db_session):
    funcionario = criar_funcionario(db_session)

    resposta = client.post(
        "/auth/login",
        json={"login": funcionario.login, "password": "senha123", "type": "funcionario"},
    )

    assert resposta.status_code == 200
    assert "token" in resposta.json()


def test_login_via_api_com_senha_errada(client, db_session):
    funcionario = criar_funcionario(db_session)

    resposta = client.post(
        "/auth/login",
        json={"login": funcionario.login, "password": "senha-errada", "type": "funcionario"},
    )

    assert resposta.status_code == 401


def test_login_via_api_sem_informar_type_assume_cliente(client, db_session):
    funcionario = criar_funcionario(db_session)

    # LoginSchema.type é opcional; quando não vem, authenticate() trata
    # como "cliente" -- ou seja, login de funcionário sem `type` deve falhar.
    resposta = client.post(
        "/auth/login",
        json={"login": funcionario.login, "password": "senha123"},
    )

    assert resposta.status_code == 401
