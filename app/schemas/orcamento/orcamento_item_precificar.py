from pydantic import BaseModel, ConfigDict

class OrcamentoItemPrecificar(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    preco_unitario: float
