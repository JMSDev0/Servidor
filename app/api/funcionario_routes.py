from app.service.funcionario_service import FuncionarioService
from fastapi import APIRouter, Depends
from app.schemas.funcionario.funcionario_create import FuncionarioCreate
from app.schemas.funcionario.funcionario_edit import FuncionarioEdit
from app.schemas.funcionario.funcionario_response import FuncionarioResponse
from app.enums.tipo_funcionario import TipoFuncionario
from app.service.auth_service import verify_token, require_funcionario
from uuid import UUID

funcionario_routes = APIRouter(dependencies=[Depends(require_funcionario)])
funcionario_service = FuncionarioService()

@funcionario_routes.post("", response_model=FuncionarioResponse)
async def create_funcionario(
    funcionario: FuncionarioCreate,
    current_user: dict = Depends(verify_token),
):
    return funcionario_service.save(funcionario, current_user)

@funcionario_routes.put("/{id}", response_model=FuncionarioResponse)
async def update_funcionario(
    id: UUID,
    funcionario: FuncionarioEdit,
    current_user: dict = Depends(verify_token),
):
    return funcionario_service.update(id, funcionario, current_user)

@funcionario_routes.delete("/{id}", response_model=dict[str, str])
async def soft_delete_funcionario(
    id: UUID,
    current_user: dict = Depends(verify_token),
):
    funcionario_service.soft_delete(id, current_user)
    return {"message": "Funcionário desativado com sucesso."}

@funcionario_routes.get("/check-token", response_model=dict[str, str])
async def check_token(current_user: dict = Depends(verify_token)):
    return {"message": "Token válido.", "login": current_user["login"], "type": current_user["type"], "name": current_user["name"]}

@funcionario_routes.get("/find")
async def find_funcionarios(
    page: int = 0,
    size: int = 10,
    nome: str | None = None,
    cpf: str | None = None,
    email: str | None = None,
    login: str | None = None,
    tipo: TipoFuncionario | None = None,
    ativo: bool | None = None,
    current_user: dict = Depends(verify_token),
):
    filters = {
        "nome": nome,
        "cpf": cpf,
        "email": email,
        "login": login,
        "tipo": tipo,
        "ativo": ativo,
    }

    filters = {
        key: value
        for key, value in filters.items()
        if value is not None
    }

    return funcionario_service.find_funcionarios(
        page=page,
        size=size,
        filters=filters,
        current_user=current_user,
    )

@funcionario_routes.get("/resume")
async def get_resume(current_user: dict = Depends(verify_token)):
    return funcionario_service.get_resume(current_user)
