from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import date, datetime
from app.enums.orcamento_enums import OrcamentoStatus
from app.schemas.orcamento.item_orcamento_response import ItemOrcamentoResponse
from app.schemas.cliente.cliente_response import ClienteResponse

class OrcamentoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_orcamento: UUID
    status: OrcamentoStatus
    valor_total: float
    data_validade: date | None
    criado_em: datetime
    atualizado_em: datetime
    id_cliente: UUID | None
    id_funcionario: UUID | None
    id_empresa_contrato: UUID | None
    itens: list[ItemOrcamentoResponse]
    cliente: ClienteResponse | None = None
