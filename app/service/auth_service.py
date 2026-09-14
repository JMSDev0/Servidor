from app.models.funcionario import Funcionario
from app.models.cliente import Cliente
from app.enums.tipo_funcionario import TipoFuncionario
import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, Header, Depends
import os
from datetime import datetime, timedelta
from app.exceptions.exceptions import UnauthorizedException
from app.db.config import get_db_session
from app.util.repo_factory import RepoFactory
from app.repository.user_repository import UserRepository
from app.util.hash import verify_password

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
MINUTOS_VALIDADE_TOKEN_PRIMEIRO_ACESSO = 30

def authenticate(login: str, password: str, type: str):
    if type == "funcionario":
        from app.service.funcionario_service import FuncionarioService

        funcionario_service = FuncionarioService()
        funcionario = funcionario_service.get_by_login(login)
        if funcionario and funcionario.ativo and verify_password(password, funcionario.senha_hash):
            return _generate_token(funcionario, type)
    elif type == "cliente":
        from app.service.cliente_service import ClienteService

        cliente_service = ClienteService()
        cliente = cliente_service.get_by_login(login)
        if cliente and cliente.ativo and verify_password(password, cliente.senha_hash):
            return _generate_token(cliente, type)
    return False

def _generate_token(user: Funcionario | Cliente, type: str | None):
    payload = None
    if type == "funcionario":
        payload = {
            'login': user.login,
            'name': user.nome,
            'type': user.tipo.value,
        }
    elif type == "cliente":
        payload = {
            'login': user.login,
            'name': user.nome,
            "type": "cliente"
        }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token, payload

def generate_primeiro_acesso_token(cliente: Cliente):
    payload = {
        'id_cliente': str(cliente.id_cliente),
        'purpose': 'primeiro_acesso',
        'exp': datetime.utcnow() + timedelta(minutes=MINUTOS_VALIDADE_TOKEN_PRIMEIRO_ACESSO),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_primeiro_acesso_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Token de primeiro acesso expirado.")
    except jwt.InvalidTokenError:
        raise UnauthorizedException("Token de primeiro acesso inválido.")
    if payload.get('purpose') != 'primeiro_acesso':
        raise UnauthorizedException("Token inválido para esta operação.")
    return payload['id_cliente']

def get_current_cliente(current_user: dict):
    if not current_user or current_user.get("type") != "cliente":
        raise UnauthorizedException("Acesso não autorizado. Usuário não é um cliente.")
    with get_db_session() as db:
        repo_class = RepoFactory.get_repository("cliente")
        repo_instance: UserRepository = repo_class(db)
        cliente = repo_instance.get_by_login(current_user.get("login"))
    if not cliente:
        raise UnauthorizedException("Acesso não autorizado. Cliente não encontrado.")
    return cliente

def verify_token(authorization: str = Header(...)):
    token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization
    payload = _decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload

def _decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def check_user_permission(current_user: dict, required_roles: set | None = None, repo: str | None = None):
    if not current_user:
        raise UnauthorizedException("Acesso não autorizado. Usuário não autenticado.")
    if current_user.get("type") == "cliente" and repo != "cliente":
        raise UnauthorizedException("Acesso não autorizado. Usuário não é um funcionário.")
    user = None
    if repo:
        with get_db_session() as db:
            repo_class = RepoFactory.get_repository(repo)
            repo_instance: UserRepository = repo_class(db)
            user = repo_instance.get_by_login(current_user.get("login"))
    if not user:
        raise UnauthorizedException("Acesso não autorizado. Funcionário não encontrado.")
    if not required_roles:
        return user
    if user.tipo != TipoFuncionario.ADMIN and user.tipo.value not in required_roles:
        raise UnauthorizedException("Você não tem permissão para realizar esta ação.")
    return user

def require_funcionario(current_user: dict = Depends(verify_token)):
    """
    Dependency de router: usar em `APIRouter(dependencies=[Depends(require_funcionario)])`
    pra bloquear qualquer rota interna pra token de cliente, sem precisar repetir
    check_user_permission em cada método de service. Os services continuam chamando
    check_user_permission também — essa dependency é uma camada extra, não substitui.
    """
    return check_user_permission(current_user, repo="funcionario")
