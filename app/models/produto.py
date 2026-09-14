from app.db.config import Base
from sqlalchemy import Column, VARCHAR, BOOLEAN, ForeignKey, DECIMAL, func, Enum, INTEGER
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
from uuid import uuid4
from app.enums.tipo_producao import TipoProducao


class Produto(Base):
    __tablename__ = "produto"
    id_produto = Column(UUID, primary_key=True, default=uuid4)
    nome = Column(VARCHAR(150), nullable=False)
    descricao = Column(VARCHAR(700))
    preco = Column(DECIMAL(10,2), nullable=False)
    quantidade_estoque = Column(INTEGER, nullable=False)

    tipo_producao = Column(Enum(TipoProducao), default=TipoProducao.PRONTO)

    ativo = Column(BOOLEAN, nullable=False, default=True)
    criado_em = Column(TIMESTAMP, nullable=False, server_default=func.now())
    atualizado_em = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    id_categoria = Column(UUID, ForeignKey("categoria.id_categoria", ondelete="SET NULL"), nullable=True)

    imagem_url = Column(VARCHAR(500), nullable=True)

    categoria = relationship("Categoria")

    fornecedores = relationship("ProdutoFornecedor", back_populates="produto", cascade="all, delete-orphan")

    avaliacoes = relationship("Avaliacao", back_populates="produto")

    movimentacoes = relationship("MovimentacaoEstoque", back_populates="produto")
    