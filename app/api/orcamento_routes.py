from fastapi import APIRouter, Depends
from app.service.orcamento_service import OrcamentoService
from app.service.auth_service import verify_token, require_funcionario
from app.schemas.orcamento.orcamento_internal_save import OrcamentoInternalSave, OrcamentoInternalItemSave
from app.schemas.orcamento.orcamento_self_service_save import OrcamentoSelfServiceSave
from app.schemas.orcamento.orcamento_item_precificar import OrcamentoItemPrecificar
from app.schemas.orcamento.orcamento_aprovar import OrcamentoAprovar
from app.enums.orcamento_enums import OrcamentoStatus
from uuid import UUID

orcamento_router = APIRouter()
orcamento_service = OrcamentoService()

# --- rotas internas (funcionário) ---
# todo mundo aqui já passa por require_funcionario antes de chegar no endpoint,
# então nenhuma rota nova nesse router precisa se preocupar em checar isso de novo.
internal_router = APIRouter(prefix="/internal", dependencies=[Depends(require_funcionario)])

@internal_router.post("")
def create_orcamento_internal(orcamento: OrcamentoInternalSave, current_user: dict = Depends(verify_token)):
    return orcamento_service.save(orcamento, current_user, internal=True)

@internal_router.get("/aguardando-precificacao")
def listar_orcamentos_aguardando_precificacao(current_user: dict = Depends(verify_token)):
    return orcamento_service.listar_aguardando_precificacao(current_user)

@internal_router.get("/find")
def find_orcamentos(
    page: int = 0,
    size: int = 20,
    status: OrcamentoStatus | None = None,
    id_cliente: UUID | None = None,
    cliente: str | None = None,
    current_user: dict = Depends(verify_token),
):
    return orcamento_service.find(page, size, status, current_user, id_cliente, cliente)

@internal_router.get("/{id_orcamento}")
def get_orcamento_internal(id_orcamento: UUID, current_user: dict = Depends(verify_token)):
    return orcamento_service.get_orcamento_by_id_internal(id_orcamento, current_user)

@internal_router.put("/{id_orcamento}/itens")
def edit_itens_orcamento_internal(id_orcamento: UUID, itens: list[OrcamentoInternalItemSave], current_user: dict = Depends(verify_token)):
    return orcamento_service.edit_itens_orcamento(id_orcamento, itens, current_user, internal=True)

@internal_router.patch("/{id_orcamento}/itens/{id_item_orcamento}/preco")
def definir_preco_item(id_orcamento: UUID, id_item_orcamento: UUID, item: OrcamentoItemPrecificar, current_user: dict = Depends(verify_token)):
    return orcamento_service.definir_preco_item(id_orcamento, id_item_orcamento, item.preco_unitario, current_user)

@internal_router.patch("/status/{id_orcamento}")
def update_orcamento_status(
    id_orcamento: UUID,
    new_status: OrcamentoStatus,
    dados_aprovacao: OrcamentoAprovar = OrcamentoAprovar(),
    current_user: dict = Depends(verify_token),
):
    return orcamento_service.change_status(
        id_orcamento, new_status, current_user, internal=True,
        forma_pagamento=dados_aprovacao.forma_pagamento,
        id_endereco_entrega=dados_aprovacao.id_endereco_entrega,
        endereco_entrega_texto=dados_aprovacao.endereco_entrega_texto,
    )

orcamento_router.include_router(internal_router)

# --- rotas self-service (cliente) ---
@orcamento_router.post("", dependencies=[Depends(verify_token)])
def create_orcamento(orcamento: OrcamentoSelfServiceSave, current_user: dict = Depends(verify_token)):
    orcamento_internal = OrcamentoInternalSave(itens=orcamento.itens)
    return orcamento_service.save(orcamento_internal, current_user, internal=False)

@orcamento_router.get("/{id_orcamento}", dependencies=[Depends(verify_token)])
def get_orcamento(id_orcamento: UUID, current_user: dict = Depends(verify_token)):
    return orcamento_service.get_orcamento_by_id_self_service(id_orcamento, current_user)

@orcamento_router.put("/{id_orcamento}/itens", dependencies=[Depends(verify_token)])
def edit_itens_orcamento(id_orcamento: UUID, itens: list[OrcamentoInternalItemSave], current_user: dict = Depends(verify_token)):
    return orcamento_service.edit_itens_orcamento(id_orcamento, itens, current_user, internal=False)

@orcamento_router.patch("/{id_orcamento}/cancelar", dependencies=[Depends(verify_token)])
def cancelar_orcamento(id_orcamento: UUID, current_user: dict = Depends(verify_token)):
    return orcamento_service.change_status(id_orcamento, OrcamentoStatus.CANCELADO, current_user, internal=False)
