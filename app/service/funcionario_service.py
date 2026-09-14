from app.repository.funcionario_repository import FuncionarioRepository
from app.db.config import get_db_session
from app.schemas.funcionario.funcionario_create import FuncionarioCreate
from app.schemas.funcionario.funcionario_response import FuncionarioResponse
from app.schemas.funcionario.funcionario_edit import FuncionarioEdit
from app.schemas.page_model import PageModel
from app.models.funcionario import Funcionario
from app.enums.tipo_funcionario import TipoFuncionario
from validate_docbr import CPF
from app.exceptions.exceptions import EntityNotFoundException, UnauthorizedException
from app.service.auth_service import check_user_permission
from app.service.produto_service import ProdutoService
from app.service.pedido_service import PedidoService
from app.util.hash import hash_password
from uuid import UUID
from datetime import datetime

class FuncionarioService():
    def __init__(self):
        pass

    def get_by_id(self, id):
        with get_db_session() as db:
            funcionario_repository = FuncionarioRepository(db)
            return funcionario_repository.get_by_id(id)

    def save(self, funcionario: FuncionarioCreate, current_user: dict):
        func = check_user_permission(current_user, required_roles={'gestor'}, repo="funcionario")
    
        simple_funcs = [TipoFuncionario.ESTOQUISTA, TipoFuncionario.VENDEDOR]
        if func.tipo in simple_funcs:
            raise UnauthorizedException("Você não tem permissão para cadastrar funcionários")
        if func.tipo == TipoFuncionario.GESTOR and funcionario.tipo not in simple_funcs:
            raise UnauthorizedException("Você não tem permissão para cadastrar funcionários do tipo administrador ou gestor")
        
        self._create_validate(funcionario)
        funcionario_data = funcionario.model_dump()
        funcionario_data["senha_hash"] = hash_password(funcionario_data["senha"])
        funcionario_data.pop("senha", None)
        response_payload = None
        with get_db_session() as db:
            funcionario_repository = FuncionarioRepository(db)
            if funcionario_repository.get_by_cpf(funcionario_data["cpf"]):
                raise ValueError("CPF já cadastrado.")
            if funcionario_repository.get_by_email(funcionario_data["email"]):
                raise ValueError("Email já cadastrado.")
            if funcionario_repository.get_by_login(funcionario_data["login"]):
                raise ValueError("Login já cadastrado.")
            func = funcionario_repository.save(Funcionario(**funcionario_data))
            db.commit()
            response_payload = FuncionarioResponse(
                                                    id_funcionario=str(func.id_funcionario),
                                                    nome=func.nome,
                                                    cpf=func.cpf,
                                                    email=func.email,
                                                    login=func.login,
                                                    telefone=func.telefone,
                                                    endereco=func.endereco,
                                                    data_nascimento=func.data_nascimento,
                                                    salario=float(func.salario) if func.salario is not None else None,
                                                    tipo=func.tipo.value if hasattr(func.tipo, "value") else func.tipo,
                                                    comissao_percentual=float(func.comissao_percentual) if func.comissao_percentual is not None else None,
                                                    ativo=func.ativo,
                                                    criado_em=func.criado_em,
                                                    atualizado_em=func.atualizado_em
                                                    )
        return response_payload

    def update(self, id: UUID, funcionario: FuncionarioEdit, current_user: dict):
        actor = check_user_permission(current_user, required_roles={'gestor'}, repo="funcionario")
        with get_db_session() as db:
            funcionario_repository = FuncionarioRepository(db)
            func = funcionario_repository.get_by_id(id)
            if not func:
                raise EntityNotFoundException(f"Funcionário com ID {id} não encontrado.")
            # Mesma hierarquia de save(): GESTOR só administra ESTOQUISTA/VENDEDOR,
            # não pode editar admin/gestor nem promover ninguém a esses cargos.
            simple_funcs = [TipoFuncionario.ESTOQUISTA, TipoFuncionario.VENDEDOR]
            if actor.tipo == TipoFuncionario.GESTOR:
                if func.tipo not in simple_funcs:
                    raise UnauthorizedException("Você não tem permissão para editar funcionários do tipo administrador ou gestor")
                if funcionario.tipo is not None and funcionario.tipo not in simple_funcs:
                    raise UnauthorizedException("Você não tem permissão para promover funcionários a administrador ou gestor")
            update_data = funcionario.model_dump(exclude_unset=True)
            if "senha" in update_data:
                update_data["senha_hash"] = hash_password(update_data["senha"])
                del update_data["senha"]
            for key, value in update_data.items():
                setattr(func, key, value)
            func.atualizado_em = datetime.now()
            db.commit()
            db.refresh(func)
            return func
        
    def get_by_login(self, login):
        with get_db_session() as db:
            funcionario_repository = FuncionarioRepository(db)
            return funcionario_repository.get_by_login(login)

    def soft_delete(self, id, current_user: dict):
        actor = check_user_permission(current_user, required_roles={'gestor'}, repo="funcionario")
        with get_db_session() as db:
            funcionario_repository = FuncionarioRepository(db)
            funcionario = funcionario_repository.get_by_id(id)
            if not funcionario:
                raise EntityNotFoundException(id)
            if actor.tipo == TipoFuncionario.GESTOR and funcionario.tipo not in [TipoFuncionario.ESTOQUISTA, TipoFuncionario.VENDEDOR]:
                raise UnauthorizedException("Você não tem permissão para desativar funcionários do tipo administrador ou gestor")
            funcionario.ativo = False
            db.commit()
            return True

    def _create_validate(self, funcionario: FuncionarioCreate):
        cpf_validator = CPF()
        if not cpf_validator.validate(funcionario.cpf):
            raise ValueError("CPF inválido.")
        if not funcionario.nome or not funcionario.cpf or not funcionario.email or not funcionario.login or not funcionario.senha:
            raise ValueError("Todos os campos obrigatórios devem ser preenchidos.")
        if len(funcionario.senha) < 6:
            raise ValueError("A senha deve ter pelo menos 6 caracteres.")
        if funcionario.salario is not None and funcionario.salario < 0:
            raise ValueError("O salário não pode ser negativo.")
        if funcionario.comissao_percentual and funcionario.tipo != TipoFuncionario.VENDEDOR:
            raise ValueError("A comissão percentual só pode ser definida para funcionários do tipo 'vendedor'.")
        if funcionario.comissao_percentual is not None and (funcionario.comissao_percentual < 0 or funcionario.comissao_percentual > 100):
            raise ValueError("A comissão percentual deve estar entre 0 e 100.")

    def find_funcionarios(
        self,
        page: int = 0,
        size: int = 20,
        filters: dict = None,
        current_user: dict = None
    ):
        func = check_user_permission(
            current_user,
            required_roles={"gestor"},
            repo="funcionario"
        )

        if func.tipo == TipoFuncionario.GESTOR:

            if filters is None:
                filters = {}

            allowed_types = [
                TipoFuncionario.ESTOQUISTA,
                TipoFuncionario.VENDEDOR
            ]

            if "tipo" in filters:
                if filters["tipo"] in allowed_types:
                    filters["tipo"] = [filters["tipo"]]
                else:
                    filters["tipo"] = []
            else:
                filters["tipo"] = allowed_types

        with get_db_session() as db:
            funcionario_repository = FuncionarioRepository(db)

            funcionarios, total_count = (
                funcionario_repository.find_funcionarios(
                    int(page),
                    int(size),
                    filters or {}
                )
            )

            content = [
                FuncionarioResponse(
                    id_funcionario=str(func.id_funcionario),
                    nome=func.nome,
                    cpf=func.cpf,
                    email=func.email,
                    login=func.login,
                    telefone=func.telefone,
                    endereco=func.endereco,
                    data_nascimento=func.data_nascimento,
                    salario=float(func.salario)
                        if func.salario is not None else None,
                    tipo=func.tipo.value
                        if hasattr(func.tipo, "value") else func.tipo,
                    comissao_percentual=float(func.comissao_percentual)
                        if func.comissao_percentual is not None else None,
                    ativo=func.ativo,
                    criado_em=func.criado_em,
                    atualizado_em=func.atualizado_em
                )
                for func in funcionarios
            ]

            return PageModel(
                content=content,
                total_items=total_count,
                total_pages=total_count // size
                    + (1 if total_count % size > 0 else 0),
                page=page,
                size=size
            )

    def get_resume(self, current_user: dict):
        func = check_user_permission(
            current_user,
            repo="funcionario"
        )

        with get_db_session() as db:
            produto_service = ProdutoService()
            in_stock = produto_service.get_quantity_produtos_in_stock()
            pedido_service = PedidoService()
            total_sales = pedido_service.get_mouth_sales(current_user)
            return {
                "total_produtos_estoque": in_stock,
                "total_vendas_mes": total_sales,
                "tickets": 0
            }
    