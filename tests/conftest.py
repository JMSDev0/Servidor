"""
Configuração dos testes.

Antes de qualquer teste rodar, a gente troca o banco "de verdade" (Postgres)
por um banco SQLite que existe só na memória do computador. Assim os testes
rodam rápido, não precisam de um Postgres instalado, e cada teste sempre
começa com o banco vazio.

Esse arquivo se chama "conftest.py" por convenção do pytest: qualquer coisa
definida aqui (as funções com @pytest.fixture) fica disponível pra todos os
arquivos de teste da pasta, sem precisar importar.
"""
import os

# Isso precisa ser definido ANTES de importar qualquer coisa do app, porque
# app/db/config.py lê essas variáveis assim que é importado.
os.environ.setdefault("DB_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "chave-secreta-de-teste-com-32-caracteres")
os.environ.setdefault("SERVER_TYPE", "default")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

import app.db.config as db_config

# check_same_thread=False + StaticPool: o TestClient do FastAPI chama a API
# em outra thread. Um SQLite "em memória" comum criaria um banco novo (e
# vazio) pra cada thread; com essas duas opções, todo mundo usa a mesma
# conexão, e por consequência o mesmo banco.
engine_de_teste = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
db_config.engine = engine_de_teste
db_config.sessionMaker = sessionmaker(bind=engine_de_teste)

import app.models  # noqa: F401 (necessário: registra todas as tabelas)


@pytest.fixture(autouse=True)
def banco_limpo():
    """
    Fixture "autouse" = roda automaticamente antes de CADA teste, sem
    precisar ser pedida. Aqui ela apaga e recria todas as tabelas, pra
    garantir que um teste nunca veja dado deixado por outro teste.
    """
    db_config.Base.metadata.drop_all(engine_de_teste)
    db_config.Base.metadata.create_all(engine_de_teste)
    yield


@pytest.fixture
def db_session():
    """
    Uma sessão do banco pra inserir dados de teste direto nas tabelas
    (sem passar pelas validações do service). Quando um teste tem
    `db_session` como parâmetro, o pytest chama essa função e entrega o
    resultado pra ele -- isso é uma "fixture".
    """
    with db_config.get_db_session() as session:
        yield session


@pytest.fixture
def client():
    """
    Cliente HTTP de teste: chama as rotas da API de verdade (com
    validação do FastAPI, autenticação, service, repository e banco),
    só que sem precisar subir um servidor numa porta de rede.
    """
    from app.api.routes import create_app

    return TestClient(create_app())
