from fastapi import APIRouter, Depends, HTTPException
from app.service.fornecedor_service import FornecedorService
from app.schemas.fornecedor.fornecedor_create import FornecedorCreate
from app.schemas.fornecedor.fornecedor_response import FornecedorResponse
from app.service.auth_service import verify_token, require_funcionario
from uuid import UUID

fornecedor_routes = APIRouter(dependencies=[Depends(require_funcionario)])
fornecedor_service = FornecedorService()

@fornecedor_routes.get("/list", response_model=list[FornecedorResponse])
async def list_all_fornecedores():
    fornecedores = fornecedor_service.list_all()
    return fornecedores

@fornecedor_routes.get("/find")
def find_fornecedores(page: int = 0, size: int = 20):
    return fornecedor_service.find(page, size)

@fornecedor_routes.get("/{id}", response_model=FornecedorResponse)
async def get_fornecedor_by_id(id: UUID):
    fornecedor = fornecedor_service.get_by_id(id)
    return fornecedor

@fornecedor_routes.post("", response_model=FornecedorResponse)
async def create_fornecedor(fornecedor: FornecedorCreate, current_user: dict = Depends(verify_token)):
    return fornecedor_service.save(fornecedor, current_user)
