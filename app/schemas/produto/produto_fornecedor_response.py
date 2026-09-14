from pydantic import BaseModel, ConfigDict
from uuid import UUID
from app.schemas.fornecedor.fornecedor_response import FornecedorResponse

class ProdutoFornecedorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_produto_fornecedor: UUID
    preco_custo: float
    id_produto: UUID
    id_fornecedor: UUID
    fornecedor: FornecedorResponse | None = None
