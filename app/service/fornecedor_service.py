from app.repository.fornecedor_repository import FornecedorRepository
from app.db.config import get_db_session
from app.exceptions.exceptions import EntityNotFoundException
from app.models.fornecedor import Fornecedor
from app.schemas.page_model import PageModel
from app.schemas.fornecedor.fornecedor_create import FornecedorCreate
from app.schemas.fornecedor.fornecedor_response import FornecedorResponse
from app.service.auth_service import check_user_permission
from validate_docbr import CNPJ

class FornecedorService():
    
    def __init__(self):
        pass

    def get_by_id(self, id):
        with get_db_session() as db:
            fornecedor_repository = FornecedorRepository(db)
            fornecedor = fornecedor_repository.get_by_id(id)
            if not fornecedor:
                raise EntityNotFoundException(id)
            return fornecedor

    def list_all(self):
        with get_db_session() as db:
            fornecedor_repository = FornecedorRepository(db)
            return fornecedor_repository.list_all()

    def find(self, page: int, size: int):
        with get_db_session() as db:
            fornecedor_repository = FornecedorRepository(db)
            fornecedores = fornecedor_repository.find(page, size)
            content = [FornecedorResponse.model_validate(fornecedor) for fornecedor in fornecedores]
            total = fornecedor_repository.count()
            return PageModel(
                content=content,
                page=page,
                size=size,
                total_pages=(total + size - 1) // size,
                total_items=total,
            )

    def save(self, fornecedor: FornecedorCreate, current_user: dict):
        check_user_permission(current_user, required_roles={'gestor'}, repo="funcionario")
        fornecedor_model = None
        with get_db_session() as db:
            fornecedor_repository = FornecedorRepository(db)
            if fornecedor_repository.get_by_cnpj(fornecedor.cnpj):
                raise ValueError("CNPJ já cadastrado.")
            self._validate_fornecedor_create(fornecedor)
            fornecedor_data = fornecedor.model_dump()
            fornecedor_model = fornecedor_repository.save(Fornecedor(**fornecedor_data))
            db.commit()
            return FornecedorResponse.model_validate(fornecedor_model)

    def _validate_fornecedor_create(self, fornecedor: FornecedorCreate):
        if not fornecedor.nome:
            raise ValueError("Nome é obrigatório")

        if not fornecedor.cnpj:
            raise ValueError("CNPJ é obrigatório")

        if not CNPJ().validate(fornecedor.cnpj):
            raise ValueError("CNPJ inválido")
        pass
        