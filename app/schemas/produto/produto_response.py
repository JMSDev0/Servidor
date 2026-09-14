from pydantic import BaseModel, ConfigDict
from uuid import UUID
from app.enums.tipo_producao import TipoProducao

class ProdutoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_produto: UUID
    nome: str
    descricao: str | None = None
    preco: float
    quantidade_estoque: int
    imagem_url: str | None = None
    tipo_producao: TipoProducao | None = None
    ativo: bool | None = None
