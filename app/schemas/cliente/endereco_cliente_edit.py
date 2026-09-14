from pydantic import BaseModel, ConfigDict

class EnderecoClienteEdit(BaseModel):
    """Edição parcial de Endereco_Cliente — mesmo padrão de FuncionarioEdit/ClienteEdit:
    todos os campos opcionais, aplicados via model_dump(exclude_unset=True) no service."""
    model_config = ConfigDict(from_attributes=True)

    apelido: str | None = None
    logradouro: str | None = None
    numero: str | None = None
    complemento: str | None = None
    bairro: str | None = None
    cidade: str | None = None
    estado: str | None = None
    cep: str | None = None
    principal: bool | None = None
