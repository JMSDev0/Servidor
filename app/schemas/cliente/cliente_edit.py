from pydantic import BaseModel, ConfigDict
from datetime import date

class ClienteEdit(BaseModel):
    model_config = ConfigDict(from_attributes=True)
     
    nome: str | None = None
    senha: str | None = None
    telefone: str | None = None
    data_nascimento: date | None = None
 