from fastapi import APIRouter, Depends, HTTPException
from app.service.auth_service import verify_token, require_funcionario
from app.schemas.cliente.cliente_save import ClienteSave
from app.schemas.cliente.cliente_edit import ClienteEdit
from app.schemas.cliente.primeiro_acesso_solicitar import PrimeiroAcessoSolicitar
from app.schemas.cliente.primeiro_acesso_confirmar import PrimeiroAcessoConfirmar
from app.service.cliente_service import ClienteService
from app.schemas.cliente.endereco_cliente import EnderecoCliente
from app.schemas.cliente.endereco_cliente_edit import EnderecoClienteEdit
from uuid import UUID

service = ClienteService()

cliente_router = APIRouter()

# --- rotas internas (funcionário) ---
internal_router = APIRouter(prefix="/internal", dependencies=[Depends(require_funcionario)])

@internal_router.post("")
def create_cliente(cliente: ClienteSave, current_user: dict = Depends(verify_token)):
    return service.save(cliente, current_user, internal=True)

@internal_router.get("/list")
def get_all_clientes(current_user: dict = Depends(verify_token)):
    return service.get_all(current_user)

@internal_router.get("/find")
def find_clientes(page: int = 0, size: int = 20, current_user: dict = Depends(verify_token)):
    return service.find(page, size, current_user)

@internal_router.delete("/{id}")
def internal_delete_cliente(id: UUID, current_user: dict = Depends(verify_token)):
    return service.soft_delete(id=id, current_user=current_user, internal=True)

@internal_router.put("/{id}")
def internal_update_cliente(id: UUID, cliente: ClienteEdit, current_user: dict = Depends(verify_token)):
    return service.update(id=id, cliente_edit=cliente, current_user=current_user, internal=True)

# --- endereços de um cliente, cadastrados/geridos por um funcionário ---
# ClienteService já suportava internal=True nesses 5 métodos (checa
# require_funcionario, não a posse do endereço) — só faltava expor rota.
@internal_router.post("/{id_cliente}/enderecos")
def internal_create_endereco(id_cliente: UUID, endereco: EnderecoCliente, current_user: dict = Depends(verify_token)):
    return service.save_endereco(endereco, cliente_id=id_cliente, current_user=current_user, internal=True)

@internal_router.get("/{id_cliente}/enderecos")
def internal_get_enderecos(id_cliente: UUID, current_user: dict = Depends(verify_token)):
    return service.get_enderecos_by_cliente_id(id_cliente=id_cliente, current_user=current_user, internal=True)

@internal_router.put("/enderecos/{id_endereco}")
def internal_update_endereco(id_endereco: UUID, endereco: EnderecoClienteEdit, current_user: dict = Depends(verify_token)):
    return service.update_endereco(id_endereco, endereco, current_user=current_user, internal=True)

@internal_router.delete("/enderecos/{id_endereco}")
def internal_delete_endereco(id_endereco: UUID, current_user: dict = Depends(verify_token)):
    service.delete_endereco(id_endereco, current_user=current_user, internal=True)
    return {"message": "Endereço deletado com sucesso."}

@internal_router.patch("/enderecos/{id_endereco}/principal")
def internal_marcar_endereco_principal(id_endereco: UUID, current_user: dict = Depends(verify_token)):
    return service.marcar_endereco_principal(id_endereco, current_user=current_user, internal=True)

cliente_router.include_router(internal_router)

# --- rotas públicas / self-service (sem precisar já estar logado) ---
@cliente_router.post("/register")
def register_cliente(cliente: ClienteSave):
    return service.register(cliente)

@cliente_router.post("/primeiro-acesso/solicitar")
def solicitar_primeiro_acesso(payload: PrimeiroAcessoSolicitar):
    token = service.solicitar_primeiro_acesso(payload.cpf_cnpj, payload.email)
    return {"token_primeiro_acesso": token}

@cliente_router.post("/primeiro-acesso/confirmar")
def confirmar_primeiro_acesso(payload: PrimeiroAcessoConfirmar):
    return service.confirmar_primeiro_acesso(payload.token, payload.senha)

@cliente_router.put("")
def update_cliente(cliente: ClienteEdit, current_user: dict = Depends(verify_token)):
    return service.update(id=None, cliente_edit=cliente, current_user=current_user)

@cliente_router.delete("")
def delete_cliente(current_user: dict = Depends(verify_token)):
    return service.soft_delete(id=None, current_user=current_user, internal=False)

@cliente_router.post("/enderecos")
def save_endereco_clientee(endereco: EnderecoCliente, current_user: dict = Depends(verify_token)):
    return service.save_endereco(endereco, current_user=current_user)

@cliente_router.get("/enderecos")
def get_enderecos_cliente(current_user: dict = Depends(verify_token)):
    return service.get_enderecos_by_cliente_id(current_user=current_user)

@cliente_router.put("/enderecos/{id}")
def update_endereco(id: UUID, endereco: EnderecoClienteEdit, current_user: dict = Depends(verify_token)):
    return service.update_endereco(id, endereco, current_user=current_user)

@cliente_router.delete("/enderecos/{id}")
def delete_endereco_cliente(id: UUID, current_user: dict = Depends(verify_token)):
    service.delete_endereco(id, current_user=current_user)
    return {"message": "Endereço deletado com sucesso."}

@cliente_router.patch("/enderecos/{id}/principal")
def marcar_endereco_principal(id: UUID, current_user: dict = Depends(verify_token)):
    return service.marcar_endereco_principal(id, current_user=current_user)