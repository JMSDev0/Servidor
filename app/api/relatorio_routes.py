from fastapi import APIRouter, Depends
from app.service.relatorio_service import RelatorioService
from app.service.auth_service import verify_token, require_funcionario
from app.schemas.relatorio.relatorio_margem_item import RelatorioMargemItem

relatorio_routes = APIRouter(dependencies=[Depends(require_funcionario)])
relatorio_service = RelatorioService()

@relatorio_routes.get("/margem", response_model=list[RelatorioMargemItem])
def relatorio_margem(current_user: dict = Depends(verify_token)):
    return relatorio_service.margem_produtos(current_user)
