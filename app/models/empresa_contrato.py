from app.db.config import Base
from sqlalchemy import Column, VARCHAR, BOOLEAN, ForeignKey, DECIMAL, func, Enum, INTEGER, DATE
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from uuid import uuid4

class EmpresaContrato(Base):
    __tablename__ = 'empresa_contrato'
    id_empresa_contrato = Column(UUID, primary_key=True, default=uuid4)
    nome = Column(VARCHAR(150), nullable=False)
    cnpj = Column(VARCHAR(20), nullable=False, unique=True)
    telefone = Column(VARCHAR(20))
    email = Column(VARCHAR(150))
    info_contrato = Column(VARCHAR(150))
    data_inicio = Column(DATE, nullable=False)
    data_fim = Column(DATE)
    contrato_ativo = Column(BOOLEAN, default=True, nullable=False)
    criado_em = Column(TIMESTAMP, nullable=False, server_default=func.now())
    