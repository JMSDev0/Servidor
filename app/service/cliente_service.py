from app.repository.cliente_repository import ClienteRepository
from app.db.config import get_db_session
from app.service.auth_service import check_user_permission, get_current_cliente, generate_primeiro_acesso_token, decode_primeiro_acesso_token
from app.schemas.cliente.cliente_save import ClienteSave
from app.schemas.cliente.cliente_response import ClienteResponse
from app.schemas.page_model import PageModel
from app.models.cliente import Cliente
from validate_docbr import CPF, CNPJ
from app.util.hash import hash_password
from uuid import UUID
from app.schemas.cliente.endereco_cliente import EnderecoCliente
from app.schemas.cliente.endereco_cliente_edit import EnderecoClienteEdit
from app.models.endereco_cliente import EnderecoCliente as EnderecoClienteModel
from app.exceptions.exceptions import ClienteJaCadastradoException
from app.schemas.cliente.cliente_edit import ClienteEdit
from app.exceptions.exceptions import RequiredFieldNotFound, EntityNotFoundException
from datetime import datetime
class ClienteService():
    def __init__(self):
        pass

    def get_by_id(self, id):
        with get_db_session() as db:
            cliente_repository = ClienteRepository(db)
            return cliente_repository.get_by_id(id)

    def get_by_login(self, login: str):
        with get_db_session() as db:
            cliente_repository = ClienteRepository(db)
            return cliente_repository.get_by_login(login)

    def register(self, cliente: ClienteSave):
        self._validate_cliente_save(cliente)
        documento = cliente.cpf or cliente.cnpj
        with get_db_session() as db:
            cliente_repository = ClienteRepository(db)
            existente = cliente_repository.get_by_documento_or_email(documento, cliente.email)
            if existente:
                raise ClienteJaCadastradoException(
                    "Já existe uma conta com esse cpf/cnpj ou email. Use o primeiro acesso pra definir sua senha."
                )
            cliente_data = cliente.model_dump()
            if cliente.cpf:
                cliente_data['cpf_cnpj'] = cliente.cpf
            elif cliente.cnpj:
                cliente_data['cpf_cnpj'] = cliente.cnpj
            cliente_data.pop('cpf', None)
            cliente_data.pop('cnpj', None)
            cliente_data["senha_hash"] = hash_password(cliente_data["senha"])
            cliente_data.pop("senha", None)
            cliente_data.pop("enderecos", None)
            cliente_model = cliente_repository.save(Cliente(**cliente_data))
            db.commit()
            for endereco in cliente.enderecos or []:
                self.save_endereco(endereco, cliente_model.id_cliente)
            return ClienteResponse.model_validate(cliente_model)

    def solicitar_primeiro_acesso(self, cpf_cnpj: str, email: str):
        with get_db_session() as db:
            cliente_repository = ClienteRepository(db)
            cliente = cliente_repository.get_by_documento_and_email(cpf_cnpj, email)
            if not cliente:
                raise ValueError("Não encontramos um cadastro com esse cpf/cnpj e email.")
            if not cliente.ativo:
                raise ValueError("Este cadastro está inativo.")
            return generate_primeiro_acesso_token(cliente)

    def confirmar_primeiro_acesso(self, token: str, nova_senha: str):
        id_cliente = decode_primeiro_acesso_token(token)
        with get_db_session() as db:
            cliente_repository = ClienteRepository(db)
            cliente = cliente_repository.get_by_id(id_cliente)
            if not cliente:
                raise ValueError("Cliente não encontrado.")
            cliente.senha_hash = hash_password(nova_senha)
            db.commit()
            return ClienteResponse.model_validate(cliente)

    def save(self, cliente: ClienteSave, current_user: dict, internal: bool = False):
        if internal:
            check_user_permission(current_user, repo="funcionario")
        self._validate_cliente_save(cliente)
        with get_db_session() as db:
            cliente_repository = ClienteRepository(db)
            if cliente_repository.get_by_login(cliente.login):
                raise ValueError("Já existe um cliente com esse login.")
            if cliente_repository.get_by_email(cliente.email):
                raise ValueError("Já existe um cliente com esse email.")   
            if cliente.cpf and cliente_repository.get_by_documento_or_email(cliente.cpf, cliente.email):
                raise ValueError("Já existe um cliente com esse CPF ou email.")
            if cliente.cnpj and cliente_repository.get_by_documento_or_email(cliente.cnpj, cliente.email):
                raise ValueError("Já existe um cliente com esse CNPJ ou email.")  
            cliente_data = cliente.model_dump()
            if cliente.cpf:
                cliente_data['cpf_cnpj'] = cliente.cpf
            elif cliente.cnpj:
                cliente_data['cpf_cnpj'] = cliente.cnpj
            cliente_data.pop('cpf', None)
            cliente_data.pop('cnpj', None)
            cliente_data["senha_hash"] = hash_password(cliente_data["senha"])
            cliente_data.pop("senha", None)
            cliente_data.pop("enderecos", None)
            cliente_model = cliente_repository.save(Cliente(**cliente_data))
            db.commit()
            for endereco in cliente.enderecos or []:
                self.save_endereco(endereco, cliente_model.id_cliente)
            return ClienteResponse.model_validate(cliente_model)

    def soft_delete(self, id: UUID | None, current_user: dict, internal: bool = False):
        client = None
        if internal:
            check_user_permission(current_user, repo="funcionario")
        else:
            client = get_current_cliente(current_user)
        with get_db_session() as db:
            cliente_repository = ClienteRepository(db)
            if id is None and client is not None:
                id = client.id_cliente
            cliente = cliente_repository.get_by_id(id)
            if not cliente:
                raise ValueError("Cliente não encontrado")
            cliente.ativo = False
            db.commit()
            return ClienteResponse.model_validate(cliente)

    def get_all(self, current_user: dict):
        check_user_permission(current_user, repo="funcionario")
        with get_db_session() as db:
            cliente_repository = ClienteRepository(db)
            clientes = cliente_repository.get_all()
            return [ClienteResponse.model_validate(cliente) for cliente in clientes]

    def find(self, page: int, size: int, current_user: dict):
        check_user_permission(current_user, repo="funcionario")
        with get_db_session() as db:
            cliente_repository = ClienteRepository(db)
            clientes = cliente_repository.find_paginated(page, size)
            total_count = cliente_repository.count()
            return PageModel(
                content=[ClienteResponse.model_validate(cliente) for cliente in clientes],
                total_items=total_count,
                page=page,
                size=size,
                total_pages=(total_count + size - 1) // size
            )

    def _validate_cliente_save(self, cliente: ClienteSave):
        if not cliente.nome:
            raise ValueError("Nome é obrigatório")

        if not cliente.cpf and not cliente.cnpj:
            raise ValueError("CPF ou CNPJ é obrigatório")

        if cliente.cpf and cliente.cnpj:
            raise ValueError("Informe apenas CPF ou CNPJ, não ambos")

        if cliente.cpf and not CPF().validate(cliente.cpf):
            raise ValueError("CPF inválido")

        if cliente.cnpj and not CNPJ().validate(cliente.cnpj):
            raise ValueError("CNPJ inválido")

        if not cliente.email:
            raise ValueError("Email é obrigatório")

        if not cliente.senha:
            raise ValueError("Senha é obrigatória")
        
        if not cliente.telefone:
            raise ValueError("Telefone é obrigatório")

        if not cliente.login:
            raise ValueError("Login é obrigatório")

    def get_enderecos_by_cliente_id(self, id_cliente: UUID | None = None, current_user: dict | None = None, internal: bool = False):
        if not internal:
            cliente = get_current_cliente(current_user)
            id_cliente = cliente.id_cliente
        else:
            check_user_permission(current_user, repo="funcionario")
            if id_cliente is None:
                raise RequiredFieldNotFound(field="id_cliente")
        with get_db_session() as db:
            cliente_repository = ClienteRepository(db)
            return cliente_repository.get_enderecos_by_cliente_id(id_cliente)

    def save_endereco(self, endereco: EnderecoCliente, cliente_id: UUID | None = None, current_user: dict | None = None, internal: bool = False):
        with get_db_session() as db:
            cliente_repository = ClienteRepository(db)
            if internal:
                if cliente_id is not None:
                    endereco.id_cliente = cliente_id
            else:
                cliente = get_current_cliente(current_user)
                endereco.id_cliente = cliente.id_cliente
            endereco_data = endereco.model_dump()
            endereco_model = cliente_repository.save_endereco(EnderecoClienteModel(**endereco_data))
            db.commit()
            db.refresh(endereco_model)
            return endereco_model

    def get_endereco_by_id(self, id_endereco: UUID):
        with get_db_session() as db:
            cliente_repository = ClienteRepository(db)
            endereco = cliente_repository.get_endereco_by_id(id_endereco)
            return endereco

    def update(self, id: UUID | None, cliente_edit: ClienteEdit, current_user: dict, internal: bool = False):
        if internal:
            if not id:
                raise RequiredFieldNotFound(field="id cliente")
            check_user_permission(current_user=current_user, repo="funcionario")
        else:
            cliente = check_user_permission(current_user=current_user, repo="cliente")
            id = cliente.id_cliente
        updated_client = None
        with get_db_session() as db:
            cliente_repository = ClienteRepository(db)
            cliente = cliente_repository.get_by_id(id)
            if not cliente:
                raise EntityNotFoundException(id)
            cliente_data = cliente_edit.model_dump(exclude_unset=True)
            if "senha" in cliente_data:
                cliente_data["senha_hash"] = hash_password(cliente_data["senha"])
                del cliente_data["senha"]
            for key, value in cliente_data.items():
                setattr(cliente, key, value)
            cliente.atualizado_em = datetime.now()
            db.commit()
            db.refresh(cliente)
            updated_client = cliente
        return ClienteResponse.model_validate(updated_client)

    def marcar_endereco_principal(self, id_endereco: UUID, current_user: dict, internal: bool = False):
        if internal:
            check_user_permission(current_user=current_user, repo="funcionario")
        else:
            cliente = get_current_cliente(current_user)
        endereco_data = None
        with get_db_session() as db:
            cliente_repository = ClienteRepository(db)
            endereco = cliente_repository.get_endereco_by_id(id_endereco)
            if not endereco:
                raise EntityNotFoundException(id_endereco)
            if not internal and endereco.id_cliente != cliente.id_cliente:
                raise ValueError("Acesso negado. Você só pode alterar seus próprios endereços.")
            cliente_repository.marcar_endereco_principal(endereco)
            endereco_data = endereco
            db.commit()
        return endereco_data
        
    def update_endereco(self, id_endereco: UUID, endereco_edit: EnderecoClienteEdit, current_user: dict, internal: bool = False):
        if internal:
            check_user_permission(current_user=current_user, repo="funcionario")
        else:
            cliente = get_current_cliente(current_user)
        updated_endereco = None
        with get_db_session() as db:
            cliente_repository = ClienteRepository(db)
            endereco = cliente_repository.get_endereco_by_id(id_endereco)
            if not endereco:
                raise EntityNotFoundException(id_endereco)
            if not internal and endereco.id_cliente != cliente.id_cliente:
                raise ValueError("Acesso negado. Você só pode alterar seus próprios endereços.")
            endereco_data = endereco_edit.model_dump(exclude_unset=True)
            for key, value in endereco_data.items():
                setattr(endereco, key, value)
            db.commit()
            db.refresh(endereco)
            updated_endereco = endereco
        return updated_endereco

    def delete_endereco(self, id_endereco: UUID, current_user: dict, internal: bool = False):
        if internal:
            check_user_permission(current_user=current_user, repo="funcionario")
        else:
            cliente = get_current_cliente(current_user)
        with get_db_session() as db:
            cliente_repository = ClienteRepository(db)
            endereco = cliente_repository.get_endereco_by_id(id_endereco)
            if not endereco:
                raise EntityNotFoundException(id_endereco)
            if not internal and endereco.id_cliente != cliente.id_cliente:
                raise ValueError("Acesso negado. Você só pode deletar seus próprios endereços.")
            if endereco.principal:
                raise ValueError("Não é possível deletar o endereço principal. Marque outro endereço como principal antes de deletar este.")
            db.delete(endereco)
            db.commit()
                        