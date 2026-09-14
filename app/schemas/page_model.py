from pydantic import BaseModel, ConfigDict
from typing import Any
from app.schemas.fornecedor.fornecedor_response import FornecedorResponse

class PageModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    page: int
    size: int
    total_pages: int
    total_items: int
    content: list[Any]
    