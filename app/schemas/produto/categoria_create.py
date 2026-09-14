from pydantic import BaseModel, ConfigDict

class CategoriaCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    nome: str
    descricao: str | None = None