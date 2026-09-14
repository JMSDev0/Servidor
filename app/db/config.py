from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager
from dotenv import load_dotenv
import os
from app.exceptions.exceptions import (
    DataBaseException,
    EntityNotFoundException,
    UnauthorizedException,
    ClienteJaCadastradoException,
    RequiredFieldNotFound,
)

load_dotenv()

DB_URL = os.getenv("DB_URL")
engine = None

SERVER_TYPE = os.getenv("SERVER_TYPE", "default")

if SERVER_TYPE == "serverless":
    engine = create_engine(
        DB_URL,
        pool_size=1,
        max_overflow=0,
        pool_pre_ping=True,
    )
elif SERVER_TYPE == "default":
    engine = create_engine(DB_URL)
else:
    raise ValueError(
        "SERVER_TYPE inválido. Use 'serverless' ou 'default'."
    )

sessionMaker = sessionmaker(autocommit=False, bind=engine)

Base = declarative_base()

@contextmanager
def get_db_session():
    session = sessionMaker()
    try:
        yield session
    except (
        EntityNotFoundException,
        UnauthorizedException,
        ClienteJaCadastradoException,
        RequiredFieldNotFound,
        ValueError,
    ):
        # Exceções de negócio da própria aplicação: cada uma já tem seu
        # handler dedicado em app/api/routes.py (400/401/404/409). Não
        # devem ser reenvelopadas em DataBaseException, senão toda
        # validação de regra de negócio vira 500 em vez do status certo.
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise DataBaseException(message=f"Erro de banco de dados.")
    finally:
        session.close()
