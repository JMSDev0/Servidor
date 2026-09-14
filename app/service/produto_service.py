from app.db.config import get_db_session
from app.repository.produto_repository import ProdutoRepository
from app.schemas.produto.produto_create import ProdutoCreate
from app.models.produto import Produto
from app.models.produto_fornecedor import ProdutoFornecedor
from app.schemas.movimentacao_estoque import MovimentacaoEstoqueCreate
from app.models.movimentacao_estoque import MovimentacaoEstoque
from app.repository.produto_fornecedor_repository import ProdutoFornecedorRepository
from app.schemas.produto.produto_fornecedor_response import ProdutoFornecedorResponse
from app.service.auth_service import check_user_permission
from app.enums.tipo_movimentacao import TipoMovimentacao
from app.exceptions.exceptions import EntityNotFoundException
from uuid import UUID

class ProdutoService():
    def __init__(self):
        pass

    def get_by_id(self, id):
        with get_db_session() as db:
            produto_repository = ProdutoRepository(db)
            return produto_repository.get_by_id(id)

    def save(self, produto: ProdutoCreate, current_user: dict):
        check_user_permission(current_user, repo="funcionario")
        self._create_validate(produto)
        produto_data = produto.model_dump()
        response_payload = None
        with get_db_session() as db:
            produto_repository = ProdutoRepository(db)
            prod = produto_repository.save(Produto(**produto_data))
            db.commit()
            db.refresh(prod)
            response_payload = prod
        return response_payload

    def update(self, id, produto: ProdutoCreate, current_user: dict):
        check_user_permission(current_user, repo="funcionario")
        self._create_validate(produto)
        produto_data = produto.model_dump()
        response_payload = None
        with get_db_session() as db:
            produto_repository = ProdutoRepository(db)
            prod = produto_repository.get_by_id(id)
            if not prod:
                raise EntityNotFoundException(id)
            for key, value in produto_data.items():
                setattr(prod, key, value)
            db.commit()
            db.refresh(prod)
            response_payload = prod
        return response_payload

    def get_all(self):
        with get_db_session() as db:
            produto_repository = ProdutoRepository(db)
            produtos = produto_repository.get_all()
            return [
                {
                    "id": prod.id_produto,
                    "nome": prod.nome,
                    "descricao": prod.descricao,
                    "preco": prod.preco,
                    "quantidade_estoque": prod.quantidade_estoque,
                    "imagem_url": prod.imagem_url,
                    "categoria": {
                        "id_categoria": prod.categoria.id_categoria,
                        "nome": prod.categoria.nome,
                        "descricao": prod.categoria.descricao
                    } if prod.categoria is not None else None
                }
                for prod in produtos
            ]

    def delete(self, id, current_user: dict):
        check_user_permission(current_user, repo="funcionario")
        with get_db_session() as db:
            produto_repository = ProdutoRepository(db)
            produto = produto_repository.get_by_id(id)
            if not produto:
                raise EntityNotFoundException(id)
            produto_repository.soft_delete(produto)
            db.commit()

    def find(self, page: int, size: int):
        with get_db_session() as db:
            produto_repository = ProdutoRepository(db)
            content = [{
                "id": prod.id_produto,
                "nome": prod.nome,
                "descricao": prod.descricao,
                "preco": prod.preco,
                "id_categoria": prod.id_categoria,
                "quantidade_estoque": prod.quantidade_estoque,
                "imagem_url": prod.imagem_url,
                "categoria": {
                    "id_categoria": prod.categoria.id_categoria,
                    "nome": prod.categoria.nome,
                    "descricao": prod.categoria.descricao
                } if prod.categoria is not None else None
            } for prod in produto_repository.find_paginated(page, size)]
            total_elements = produto_repository.count()
            return {
                "content": content,
                "total_items": total_elements,
                "total_pages": total_elements // size + (1 if total_elements % size > 0 else 0),
                "page": page,
                "size": size
            }

    def find_internal(self, page: int, size: int, current_user: dict, nome=None, id_categoria=None, tipo_producao=None, ativo=None):
        check_user_permission(current_user, repo="funcionario")
        with get_db_session() as db:
            produto_repository = ProdutoRepository(db)
            produtos = produto_repository.find_paginated_internal(page, size, nome, id_categoria, tipo_producao, ativo)
            total_elements = produto_repository.count_internal(nome, id_categoria, tipo_producao, ativo)
            content = [{
                "id": prod.id_produto,
                "nome": prod.nome,
                "descricao": prod.descricao,
                "preco": prod.preco,
                "id_categoria": prod.id_categoria,
                "quantidade_estoque": prod.quantidade_estoque,
                "imagem_url": prod.imagem_url,
                "ativo": prod.ativo,
                "tipo_producao": prod.tipo_producao.value if prod.tipo_producao else None,
                "categoria": {
                    "id_categoria": prod.categoria.id_categoria,
                    "nome": prod.categoria.nome,
                    "descricao": prod.categoria.descricao
                } if prod.categoria is not None else None
            } for prod in produtos]
            return {
                "content": content,
                "total_items": total_elements,
                "total_pages": (total_elements // size + (1 if total_elements % size > 0 else 0)) if size else 0,
                "page": page,
                "size": size
            }

    def _create_validate(self, produto: ProdutoCreate):
        if not produto.nome:
            raise ValueError("Nome é obrigatório")

        if not isinstance(produto.preco, (int, float)) or produto.preco < 0:
            raise ValueError("Preço deve ser um número positivo")

        if not isinstance(produto.quantidade_estoque, int) or produto.quantidade_estoque < 0:
            raise ValueError("Quantidade em estoque deve ser um número inteiro não negativo")

    def associate_fornecedor(self, id_produto: UUID, id_fornecedor: UUID, preco_custo: float, current_user: dict):
        check_user_permission(current_user, repo="funcionario")
        with get_db_session() as db:
            produto_fornecedor_repository = ProdutoFornecedorRepository(db)
            produto_fornecedor = ProdutoFornecedor(
                id_produto=id_produto,
                id_fornecedor=id_fornecedor,
                preco_custo=preco_custo
            )
            produto_fornecedor_repository.save(produto_fornecedor)
            db.commit()
            # get_by_id (com joinedload em fornecedor) em vez de db.refresh:
            # refresh só recarrega colunas simples, não relações — sem isso
            # `fornecedor` nunca apareceria na resposta, igual ao bug que já
            # vimos em Pedido.itens.
            atualizado = produto_fornecedor_repository.get_by_id(
                produto_fornecedor.id_produto_fornecedor
            )
            return ProdutoFornecedorResponse.model_validate(atualizado)

    def list_fornecedores(self, id_produto: UUID, current_user: dict = None):
        if current_user:
            check_user_permission(current_user, repo="funcionario")
        with get_db_session() as db:
            produto_fornecedor_repository = ProdutoFornecedorRepository(db)
            associacoes = produto_fornecedor_repository.get_by_produto(id_produto)
            return [ProdutoFornecedorResponse.model_validate(a) for a in associacoes]

    def list_produtos_by_fornecedor(self, id_fornecedor: UUID, current_user: dict = None):
        if current_user:
            check_user_permission(current_user, repo="funcionario")
        with get_db_session() as db:
            produto_repository = ProdutoRepository(db)
            return produto_repository.get_by_fornecedor(id_fornecedor)
        

    def register_stock_movement(self, mov: MovimentacaoEstoqueCreate):
        with get_db_session() as db:
            produto_repository = ProdutoRepository(db)
            mov_dict = mov.model_dump()
            movimentacao_model = produto_repository.register_stock_movement(MovimentacaoEstoque(**mov_dict))
            produto = produto_repository.get_by_id(mov.id_produto)
            if mov.tipo_movimentacao == TipoMovimentacao.ENTRADA:
                produto.quantidade_estoque += mov.quantidade
            elif mov.tipo_movimentacao == TipoMovimentacao.SAIDA:
                if produto.quantidade_estoque < mov.quantidade:
                    raise ValueError("Quantidade em estoque insuficiente para a saída")
                produto.quantidade_estoque -= mov.quantidade
            else:
                raise ValueError("Tipo de movimentação inválido")
            db.commit()
            db.refresh(movimentacao_model)
            return movimentacao_model


    def get_stock_movements(self, id_produto: UUID, current_user: dict = None):
        if current_user:
            check_user_permission(current_user, repo="funcionario")
        with get_db_session() as db:
            produto_repository = ProdutoRepository(db)
            return produto_repository.get_movimentacoes_by_produto(id_produto)

    def get_quantity_produtos_in_stock(self):
        with get_db_session() as db:
            produto_repository = ProdutoRepository(db)
            return produto_repository.get_quantity_produtos_in_stock()
    