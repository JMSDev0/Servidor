"""
Funções auxiliares pra criar dados de teste direto no banco.

Isso aqui NÃO é fixture do pytest -- são só funções Python normais, que
cada teste chama explicitamente quando precisa. A ideia é deixar bem claro,
lendo o teste de cima pra baixo, o que foi criado e com quais dados.
"""
from datetime import date

from app.enums.tipo_funcionario import TipoFuncionario
from app.models.categoria import Categoria
from app.models.empresa_contrato import EmpresaContrato
from app.models.fornecedor import Fornecedor
from app.models.funcionario import Funcionario
from app.models.cliente import Cliente
from app.enums.tipo_producao import TipoProducao
from app.models.produto import Produto
from app.models.produto_fornecedor import ProdutoFornecedor
from app.util.hash import hash_password

SENHA_PADRAO_DE_TESTE = "senha123"

# CNPJs válidos (checksum ok) só pra teste -- não pertencem a empresas reais.
CNPJ_VALIDO_1 = "11222333000181"
CNPJ_VALIDO_2 = "25176957518482"


def criar_funcionario(db_session, tipo: TipoFuncionario = TipoFuncionario.ADMIN, senha: str = SENHA_PADRAO_DE_TESTE):
    """Insere um Funcionario direto no banco, já com a senha 'hasheada'."""
    funcionario = Funcionario(
        nome="Funcionario de Teste",
        cpf="12345678900",
        email="funcionario@teste.com",
        login="funcionario_teste",
        senha_hash=hash_password(senha),
        telefone="11999999999",
        endereco="Rua de Teste, 123",
        salario=2000,
        tipo=tipo,
    )
    db_session.add(funcionario)
    db_session.commit()
    return funcionario


def criar_categoria(db_session, nome: str = "Categoria de Teste"):
    """Insere uma Categoria direto no banco (produto exige uma categoria).
    Get-or-create: `nome` é único (RN-CAT-01), e testes que criam mais de um
    produto no mesmo teste (ex: relatório de margem) chamam isso mais de uma
    vez -- reaproveita a categoria já existente em vez de colidir."""
    existente = db_session.query(Categoria).filter(Categoria.nome == nome).first()
    if existente:
        return existente
    categoria = Categoria(nome=nome)
    db_session.add(categoria)
    db_session.commit()
    return categoria

def criar_cliente(db_session):
    cliente = Cliente(
        nome="Teste",
        cpf_cnpj="186.693.266-71",
        email="t@t.com",
        senha_hash=hash_password("123"),
        login="t",
        telefone="3199999999"
    )
    db_session.add(cliente)
    db_session.commit()
    return cliente



def criar_fornecedor(db_session, cnpj: str | None = None):
    """cnpj=None gera um CNPJ válido novo a cada chamada (cnpj é único na
    tabela) -- só passe um fixo se o teste precisar saber o valor exato."""
    if cnpj is None:
        from validate_docbr import CNPJ as CNPJValidator
        cnpj = CNPJValidator().generate()
    fornecedor = Fornecedor(nome="Fornecedor de Teste", cnpj=cnpj)
    db_session.add(fornecedor)
    db_session.commit()
    return fornecedor


def criar_produto(
    db_session,
    preco: float = 100.0,
    quantidade_estoque: int = 10,
    custo: float | None = None,
    tipo_producao: TipoProducao = TipoProducao.PRONTO,
):
    """Insere um Produto direto no banco. Se `custo` for informado, também
    cria um Fornecedor e vincula via ProdutoFornecedor (produto_fornecedor.preco_custo)."""
    categoria = criar_categoria(db_session)
    produto = Produto(
        nome="Produto de Teste",
        preco=preco,
        quantidade_estoque=quantidade_estoque,
        id_categoria=categoria.id_categoria,
        tipo_producao=tipo_producao,
    )
    db_session.add(produto)
    db_session.commit()

    if custo is not None:
        fornecedor = criar_fornecedor(db_session)
        db_session.add(ProdutoFornecedor(id_produto=produto.id_produto, id_fornecedor=fornecedor.id_fornecedor, preco_custo=custo))
        db_session.commit()
        db_session.refresh(produto)

    return produto


def criar_empresa_contrato(db_session, cnpj: str = CNPJ_VALIDO_1, contrato_ativo: bool = True):
    empresa = EmpresaContrato(
        nome="Empresa Parceira de Teste",
        cnpj=cnpj,
        data_inicio=date(2024, 1, 1),
        contrato_ativo=contrato_ativo,
    )
    db_session.add(empresa)
    db_session.commit()
    return empresa


def usuario_logado(funcionario: Funcionario):
    """
    Monta o dict que o service espera receber como `current_user`.

    É o mesmo formato que o app usa quando decodifica o token JWT de quem
    está logado -- aqui a gente monta ele "na mão" pra testar o service
    sem precisar passar por login/JWT de verdade.
    """
    return {"login": funcionario.login, "type": funcionario.tipo.value}

