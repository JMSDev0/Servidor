from pydantic import BaseModel, ConfigDict
from uuid import UUID

class OrcamentoInternalItemSave(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_produto: UUID
    quantidade: int
    # Obrigatório apenas para produtos sob_medida, preenchido pelo vendedor
    # (funcionário) ao montar o orçamento. Ignorado para produtos prontos,
    # que sempre usam o preço de catálogo do produto.
    preco_unitario: float | None = None


class OrcamentoInternalSave(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_cliente: UUID | None = None
    id_empresa_contrato: UUID | None = None
    itens: list[OrcamentoInternalItemSave]

