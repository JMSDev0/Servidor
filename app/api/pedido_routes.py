from fastapi import APIRouter, Depends
from app.service.auth_service import verify_token, require_funcionario
from app.service.pedido_service import PedidoService
from app.schemas.pedido.pedido_create import PedidoCreate
from app.enums.pedido_enums import StatusPedido
from uuid import UUID
pedido_router = APIRouter()
internal_router = APIRouter(prefix="/internal", dependencies=[Depends(require_funcionario)])

pedido_service = PedidoService()

@internal_router.post("")
def create_pedido(pedido: PedidoCreate, current_user: dict = Depends(verify_token)):
    return pedido_service.save(pedido, current_user, internal=True)

@internal_router.get("/find")
def find_pedidos(
    page: int = 0,
    size: int = 20,
    status: StatusPedido | None = None,
    id_cliente: UUID | None = None,
    cliente: str | None = None,
    current_user: dict = Depends(verify_token),
):
    return pedido_service.find(page, size, status, current_user, id_cliente, cliente)

@internal_router.get("/{id}")
def get_pedido(id: UUID, current_user: dict = Depends(verify_token)):
    return pedido_service.get_by_id(id, current_user)

@internal_router.put("/{id}/status")
def change_pedido_status(id: UUID, status: StatusPedido, current_user: dict = Depends(verify_token)):
    return pedido_service.update_status(id, status, current_user)

@internal_router.get("/get-by-cliente/{id_cliente}")
def get_pedidos_by_cliente(id_cliente: UUID, current_user: dict = Depends(verify_token)):
    return pedido_service.get_by_cliente(id_cliente=id_cliente, current_user=current_user, internal=True)

pedido_router.include_router(internal_router)

@pedido_router.get("/get-by-cliente")
def get_pedidos_by_cliente(current_user: dict = Depends(verify_token)):
    return pedido_service.get_by_cliente(current_user=current_user)