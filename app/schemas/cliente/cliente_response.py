from pydantic import BaseModel, ConfigDict
from datetime import date
from uuid import UUID


class ClienteEnderecoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_endereco: UUID
    apelido: str | None = None
    logradouro: str
    numero: str | None = None
    complemento: str | None = None
    bairro: str
    cidade: str
    estado: str
    cep: str
    principal: bool | None = False
    

class ClienteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_cliente: UUID
    nome: str
    cpf_cnpj: str
    email: str
    login: str
    telefone: str | None = None
    data_nascimento: date | None = None
    enderecos: list[ClienteEnderecoResponse] | None = None

    