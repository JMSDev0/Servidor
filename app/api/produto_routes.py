from fastapi import APIRouter, Depends
from app.service.categoria_produto_service import CategoriaProdutoService
from app.schemas.produto.categoria_create import CategoriaCreate
from app.service.auth_service import verify_token, require_funcionario
from app.service.produto_service import ProdutoService
from app.schemas.produto.produto_create import ProdutoCreate
from app.schemas.movimentacao_estoque import MovimentacaoEstoqueCreate
from app.schemas.produto.produto_fornecedor_associate import ProdutoFornecedorAssociate
from app.enums.tipo_producao import TipoProducao
from uuid import UUID

produto_router = APIRouter()

categoria_produto_service = CategoriaProdutoService()
produto_service = ProdutoService()

# --- rotas internas (funcionário) ---
internal_router = APIRouter(prefix="/internal", dependencies=[Depends(require_funcionario)])

@internal_router.post("")
def create_produto(produto: ProdutoCreate, current_user: dict = Depends(verify_token)):
    return produto_service.save(produto, current_user)

@internal_router.put("/{id}")
def update_produto(id: UUID, produto: ProdutoCreate, current_user: dict = Depends(verify_token)):
    return produto_service.update(id, produto, current_user)

@internal_router.delete("/{id}")
def delete_produto(id: UUID, current_user: dict = Depends(verify_token)):
    produto_service.delete(id, current_user)
    return {"message": "Produto deletado com sucesso"}

@internal_router.post("/fornecedor")
def add_produto_fornecedor(associate: ProdutoFornecedorAssociate, current_user: dict = Depends(verify_token)):
    return produto_service.associate_fornecedor(associate.id_produto, associate.id_fornecedor, associate.preco_custo, current_user)

@internal_router.get("/fornecedor/{id_produto}")
def list_produto_fornecedores(id_produto: UUID, current_user: dict = Depends(verify_token)):
    return produto_service.list_fornecedores(id_produto, current_user)

@internal_router.post("/categoria")
def create_categoria(categoria: CategoriaCreate, current_user: dict = Depends(verify_token)):
    return categoria_produto_service.save(categoria, current_user)

@internal_router.delete("/categoria/{id}")
def delete_categoria(id: UUID, current_user: dict = Depends(verify_token)):
    categoria_produto_service.delete(id, current_user)
    return {"message": "Categoria deletada com sucesso"}

@internal_router.post("/movimentacao")
def register_stock_movement(mov: MovimentacaoEstoqueCreate, current_user: dict = Depends(verify_token)):
    return produto_service.register_stock_movement(mov)

@internal_router.get("/movimentacao/{id_produto}")
def list_stock_movements(id_produto: UUID, current_user: dict = Depends(verify_token)):
    return produto_service.get_stock_movements(id_produto, current_user)

@internal_router.get("/fornecedor/{id_fornecedor}/produtos")
def list_produtos_by_fornecedor(id_fornecedor: UUID, current_user: dict = Depends(verify_token)):
    return produto_service.list_produtos_by_fornecedor(id_fornecedor, current_user)

@internal_router.get("/find")
def find_produtos_internal(
    page: int = 0,
    size: int = 20,
    nome: str | None = None,
    id_categoria: UUID | None = None,
    tipo_producao: TipoProducao | None = None,
    ativo: bool | None = None,
    current_user: dict = Depends(verify_token),
):
    return produto_service.find_internal(page, size, current_user, nome, id_categoria, tipo_producao, ativo)


produto_router.include_router(internal_router)

# --- rotas públicas (catálogo da loja) ---
@produto_router.get("/list")
def get_all_produtos():
    return produto_service.get_all()

@produto_router.get("/find")
def find_produtos(page: int = 0, size: int = 10):
    return produto_service.find(page, size)

@produto_router.get("/categoria/list")
def get_all_categorias():
    return categoria_produto_service.get_all()

@produto_router.get("/categoria/find")
def find_categorias(page: int = 0, size: int = 10):
    return categoria_produto_service.find(page, size)

@produto_router.get("/categoria/{id}", dependencies=[Depends(verify_token)])
def get_categoria_by_id(id: UUID):
    return categoria_produto_service.get_by_id(id)

@produto_router.get("/{id}", dependencies=[Depends(verify_token)])
def get_produto_by_id(id: UUID):
    return produto_service.get_by_id(id)
