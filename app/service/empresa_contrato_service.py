from app.db.config import get_db_session
from app.exceptions.exceptions import EntityNotFoundException
from app.models.empresa_contrato import EmpresaContrato
from app.repository.empresa_contrato_repository import EmpresaContratoRepository
from app.schemas.empresa.empresa_contrato_create import EmpresaContratoCreate
from app.schemas.empresa.empresa_contrato_response import EmpresaContratoResponse
from app.schemas.empresa.empresa_contrato_update import EmpresaContratoUpdate
from app.schemas.page_model import PageModel
from app.service.auth_service import check_user_permission
from validate_docbr import CNPJ

# RN-FUN-02: gestão de contrato de empresa parceira é restrita a
# administrador/gestor (mesmo critério usado para contratos/estoque em outras
# entidades) — leitura (get_by_id/find) fica liberada pra qualquer funcionário.
CARGOS_GERENCIAM_CONTRATO = {"gestor"}


class EmpresaContratoService():

    def __init__(self):
        pass

    def get_by_id(self, id, current_user: dict):
        check_user_permission(current_user, repo="funcionario")
        with get_db_session() as db:
            empresa_contrato_repository = EmpresaContratoRepository(db)
            empresa_contrato = empresa_contrato_repository.get_by_id(id)
            if not empresa_contrato:
                raise EntityNotFoundException(id)
            return empresa_contrato

    def find(self, page: int, size: int, current_user: dict):
        check_user_permission(current_user, repo="funcionario")
        with get_db_session() as db:
            empresa_contrato_repository = EmpresaContratoRepository(db)
            empresas = empresa_contrato_repository.find_paginated(page, size)
            content = [EmpresaContratoResponse.model_validate(e) for e in empresas]
            total = empresa_contrato_repository.count()
            return PageModel(
                content=content,
                page=page,
                size=size,
                total_pages=(total + size - 1) // size if size else 0,
                total_items=total,
            )

    def save(self, empresa_contrato: EmpresaContratoCreate, current_user: dict):
        check_user_permission(current_user, required_roles=CARGOS_GERENCIAM_CONTRATO, repo="funcionario")
        self._validate_create(empresa_contrato)
        with get_db_session() as db:
            empresa_contrato_repository = EmpresaContratoRepository(db)
            if empresa_contrato_repository.get_by_cnpj(empresa_contrato.cnpj):
                raise ValueError("CNPJ já cadastrado.")
            empresa_contrato_model = empresa_contrato_repository.save(
                EmpresaContrato(**empresa_contrato.model_dump())
            )
            db.commit()
            return EmpresaContratoResponse.model_validate(empresa_contrato_model)

    def update(self, id, dados: EmpresaContratoUpdate, current_user: dict):
        check_user_permission(current_user, required_roles=CARGOS_GERENCIAM_CONTRATO, repo="funcionario")
        with get_db_session() as db:
            empresa_contrato_repository = EmpresaContratoRepository(db)
            empresa_contrato = empresa_contrato_repository.get_by_id(id)
            if not empresa_contrato:
                raise EntityNotFoundException(id)

            for campo, valor in dados.model_dump(exclude_unset=True).items():
                setattr(empresa_contrato, campo, valor)

            if empresa_contrato.data_fim and empresa_contrato.data_fim < empresa_contrato.data_inicio:
                raise ValueError("data_fim não pode ser anterior a data_inicio.")

            db.commit()
            db.refresh(empresa_contrato)
            return EmpresaContratoResponse.model_validate(empresa_contrato)

    def _validate_create(self, empresa_contrato: EmpresaContratoCreate):
        if not empresa_contrato.nome:
            raise ValueError("Nome é obrigatório.")

        if not empresa_contrato.cnpj:
            raise ValueError("CNPJ é obrigatório.")

        if not CNPJ().validate(empresa_contrato.cnpj):
            raise ValueError("CNPJ inválido.")

        if empresa_contrato.data_fim and empresa_contrato.data_fim < empresa_contrato.data_inicio:
            raise ValueError("data_fim não pode ser anterior a data_inicio.")
