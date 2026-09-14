from pydantic import BaseModel, ConfigDict
from datetime import date

class EmpresaContratoCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nome: str
    cnpj: str
    telefone: str | None = None
    email: str | None = None
    info_contrato: str | None = None
    data_inicio: date
    data_fim: date | None = None
