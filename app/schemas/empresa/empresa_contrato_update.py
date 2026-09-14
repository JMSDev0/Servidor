from pydantic import BaseModel, ConfigDict
from datetime import date

class EmpresaContratoUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nome: str | None = None
    telefone: str | None = None
    email: str | None = None
    info_contrato: str | None = None
    data_fim: date | None = None
    contrato_ativo: bool | None = None
