from pydantic import BaseModel, ConfigDict
from app.schemas.orcamento.orcamento_internal_save import OrcamentoInternalItemSave

class OrcamentoSelfServiceSave(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    itens: list[OrcamentoInternalItemSave]
