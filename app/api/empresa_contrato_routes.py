from fastapi import APIRouter, Depends
from uuid import UUID
from app.service.empresa_contrato_service import EmpresaContratoService
from app.schemas.empresa.empresa_contrato_create import EmpresaContratoCreate
from app.schemas.empresa.empresa_contrato_update import EmpresaContratoUpdate
from app.schemas.empresa.empresa_contrato_response import EmpresaContratoResponse
from app.service.auth_service import verify_token, require_funcionario

empresa_contrato_routes = APIRouter(dependencies=[Depends(require_funcionario)])
empresa_contrato_service = EmpresaContratoService()

@empresa_contrato_routes.post("", response_model=EmpresaContratoResponse)
def create_empresa_contrato(empresa_contrato: EmpresaContratoCreate, current_user: dict = Depends(verify_token)):
    return empresa_contrato_service.save(empresa_contrato, current_user)

@empresa_contrato_routes.get("/find")
def find_empresas_contrato(page: int = 0, size: int = 20, current_user: dict = Depends(verify_token)):
    return empresa_contrato_service.find(page, size, current_user)

@empresa_contrato_routes.get("/{id}", response_model=EmpresaContratoResponse)
def get_empresa_contrato_by_id(id: UUID, current_user: dict = Depends(verify_token)):
    return empresa_contrato_service.get_by_id(id, current_user)

@empresa_contrato_routes.put("/{id}", response_model=EmpresaContratoResponse)
def update_empresa_contrato(id: UUID, dados: EmpresaContratoUpdate, current_user: dict = Depends(verify_token)):
    return empresa_contrato_service.update(id, dados, current_user)
