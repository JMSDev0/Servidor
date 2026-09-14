import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.auth_routes import auth
from app.api.funcionario_routes import funcionario_routes
from app.api.fornecedor_routes import fornecedor_routes
from app.api.produto_routes import produto_router
from app.api.cliente_routes import cliente_router
from app.api.pedido_routes import pedido_router
from app.api.orcamento_routes import orcamento_router
from app.api.empresa_contrato_routes import empresa_contrato_routes
from app.api.relatorio_routes import relatorio_routes
from app.exceptions.exceptions import EntityNotFoundException, UnauthorizedException, DataBaseException, ClienteJaCadastradoException, RequiredFieldNotFound
from app.api.upload_routes import upload_router

logger = logging.getLogger(__name__)

def create_app():
    app = FastAPI()
    app.add_middleware(
    CORSMiddleware,
        allow_origins=["*"],           # Habilita qualquer origem externa
        allow_credentials=False,       # OBRIGATÓRIO ser False ao usar ["*"]
        allow_methods=["*"],           # Permite todos os métodos (GET, POST, etc.)
        allow_headers=["*"],           # Permite todos os headers
    )
    _register_exception_handlers(app)
    _register_routes(app)
    return app

def _register_exception_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error during request")
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno do servidor."},
        )

    @app.exception_handler(EntityNotFoundException)
    async def entity_not_found_handler(request: Request, exc: EntityNotFoundException):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    @app.exception_handler(UnauthorizedException)
    async def unauthorized_handler(request: Request, exc: UnauthorizedException):
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DataBaseException)
    async def database_exception_handler(request: Request, exc: DataBaseException):
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ClienteJaCadastradoException)
    async def cliente_ja_cadastrado_handler(request: Request, exc: ClienteJaCadastradoException):
        return JSONResponse(
            status_code=409,
            content={"detail": str(exc), "requer_primeiro_acesso": True},
        )

    @app.exception_handler(RequiredFieldNotFound)
    async def required_field_not_found(request: Request, exc: RequiredFieldNotFound):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)}
        )

def _register_routes(app:FastAPI):
    @app.get("/", tags=["root"])
    async def root():
        return {"message": "API de Gestão de Pedidos"}
    
    @app.get("/health", tags=["health"])
    async def health():
        return {"message": "hello world"}
    app.include_router(auth, prefix="/auth", tags=["auth"])
    app.include_router(funcionario_routes, prefix="/funcionario", tags=["funcionario"])
    app.include_router(fornecedor_routes, prefix="/fornecedor", tags=["fornecedor"])
    app.include_router(produto_router, prefix="/produto", tags=["produto"])
    app.include_router(cliente_router, prefix="/cliente", tags=["cliente"])
    app.include_router(pedido_router, prefix="/pedido", tags=["pedido"])
    app.include_router(orcamento_router, prefix="/orcamento", tags=["orcamento"])
    app.include_router(empresa_contrato_routes, prefix="/empresa-contrato", tags=["empresa-contrato"])
    app.include_router(relatorio_routes, prefix="/relatorio", tags=["relatorio"])
    app.include_router(upload_router, prefix="/upload", tags=["upload"])