from app.db.config import Base
from sqlalchemy import Column, VARCHAR
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from uuid import uuid4

class Categoria(Base):
    __tablename__ = 'categoria'
    id_categoria = Column(UUID, primary_key=True, default=uuid4)
    nome = Column(VARCHAR(150), nullable=False, unique=True)
    descricao = Column(VARCHAR(150))
