from pydantic import BaseModel
from uuid import UUID

class ProdutoCreate(BaseModel):
    nome: str
    descricao: str | None = None
    preco: float
    id_categoria: UUID
    quantidade_estoque: int
    imagem_url: str | None = None
