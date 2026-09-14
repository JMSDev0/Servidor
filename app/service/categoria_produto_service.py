from app.models.categoria import Categoria
from app.db.config import get_db_session
from app.repository.categoria_produto_repository import CategoriaProdutoRepository
from app.schemas.produto.categoria_create import CategoriaCreate
from app.schemas.page_model import PageModel
from app.service.auth_service import check_user_permission
from app.exceptions.exceptions import EntityNotFoundException

class CategoriaProdutoService():
    def __init__(self):
        pass

    def get_by_id(self, id):
        with get_db_session() as db:
            categoria_produto_repository = CategoriaProdutoRepository(db)
            return categoria_produto_repository.get_by_id(id)

    def save(self, categoria: CategoriaCreate, current_user: dict):
        check_user_permission(current_user, repo="funcionario")
        self._create_validate(categoria)
        categoria_data = categoria.model_dump()
        response_payload = None
        with get_db_session() as db:
            categoria_produto_repository = CategoriaProdutoRepository(db)
            if categoria_produto_repository.get_by_nome(categoria_data["nome"]):
                raise ValueError("Categoria já cadastrada.")
            cat = categoria_produto_repository.save(Categoria(**categoria_data))
            db.commit()
            db.refresh(cat)
            response_payload = cat
        return response_payload

    def get_all(self):
        with get_db_session() as db:
            categoria_produto_repository = CategoriaProdutoRepository(db)
            return categoria_produto_repository.get_all()

    def delete(self, id, current_user: dict):
        check_user_permission(current_user, repo="funcionario")
        with get_db_session() as db:
            categoria_produto_repository = CategoriaProdutoRepository(db)
            categoria = categoria_produto_repository.get_by_id(id)
            if not categoria:
                raise EntityNotFoundException(id)
            categoria_produto_repository.delete(categoria)
            db.commit()

    def find(self, page: int, size: int):
        with get_db_session() as db:
            categoria_produto_repository = CategoriaProdutoRepository(db)
            content = [
            {
                "id_categoria": cat.id_categoria,
                "nome": cat.nome,
                "descricao": cat.descricao,
            }
            for cat in categoria_produto_repository.find_paginated(page, size)
        ]
            total_elements = categoria_produto_repository.count()
            return PageModel(
                content=content, 
                total_items=total_elements, 
                total_pages=total_elements // size + (1 if total_elements % size > 0 else 0), 
                page=page, 
                size=size
                )

    def _create_validate(self, categoria: CategoriaCreate):
        if not categoria.nome:
            raise ValueError("Nome é obrigatório")
    