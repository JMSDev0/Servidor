from pydantic import BaseModel
from datetime import date

class FornecedorCreate(BaseModel):
    nome: str
    cnpj: str
    telefone: str | None = None
    email: str | None = None
    