from app.db.config import Base
from sqlalchemy import Column, VARCHAR, BOOLEAN, ForeignKey, DECIMAL, func, Enum
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from uuid import uuid4
from app.enums.tipo_funcionario import TipoFuncionario


class Funcionario(Base):
    __tablename__ = 'funcionario'
    id_funcionario = Column(UUID, primary_key=True, default=uuid4)
    nome = Column(VARCHAR(120), nullable=False)
    cpf = Column(VARCHAR(20), nullable=False, unique=True)
    email = Column(VARCHAR(150), nullable=False, unique=True)
    senha_hash = Column(VARCHAR(255), nullable=False)
    login = Column(VARCHAR(70), nullable=False, unique=True)
    telefone = Column(VARCHAR(20), nullable=False)
    endereco = Column(VARCHAR(255), nullable=False)
    data_nascimento = Column(TIMESTAMP)

    salario = Column(DECIMAL(10, 2), nullable=False)
    tipo = Column(Enum(TipoFuncionario), nullable=False)
    comissao_percentual = Column(DECIMAL(5, 2))


    ativo = Column(BOOLEAN, nullable=False, default=True)
    criado_em = Column(TIMESTAMP, nullable=False, server_default=func.now())
    atualizado_em = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
