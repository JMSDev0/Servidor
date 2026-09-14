from pydantic import BaseModel, ConfigDict
from datetime import date
from app.schemas.cliente.endereco_cliente import EnderecoCliente

class ClienteSave(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nome: str
    cpf: str | None = None
    cnpj: str | None =  None
    email: str
    senha: str
    login: str
    telefone: str
    data_nascimento: date | None = None
    enderecos: list[EnderecoCliente] | None = None
