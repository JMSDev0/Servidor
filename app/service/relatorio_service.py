from app.db.config import get_db_session
from app.repository.produto_repository import ProdutoRepository
from app.schemas.relatorio.relatorio_margem_item import RelatorioMargemItem
from app.service.auth_service import check_user_permission

# RF16: relatório gerencial cruzando preço de venda (produto.preco) com custo
# (produto_fornecedor.preco_custo) — restrito a quem gerencia o negócio, não a
# operação do dia a dia (mesmo critério de fornecedor/RN-FUN-02).
CARGOS_VEEM_RELATORIO_GERENCIAL = {"gestor"}


class RelatorioService():

    def __init__(self):
        pass

    def margem_produtos(self, current_user: dict):
        check_user_permission(current_user, required_roles=CARGOS_VEEM_RELATORIO_GERENCIAL, repo="funcionario")
        with get_db_session() as db:
            produto_repository = ProdutoRepository(db)
            produtos = produto_repository.get_all()

            itens = []
            for produto in produtos:
                custos = [float(pf.preco_custo) for pf in produto.fornecedores]
                # Produto sem fornecedor/custo cadastrado: mostra na listagem
                # (visibilidade), mas sem margem calculável.
                custo_medio = sum(custos) / len(custos) if custos else None
                preco_venda = float(produto.preco)
                margem_valor = (preco_venda - custo_medio) if custo_medio is not None else None
                margem_percentual = (
                    (margem_valor / preco_venda * 100) if margem_valor is not None and preco_venda > 0 else None
                )
                itens.append(RelatorioMargemItem(
                    id_produto=produto.id_produto,
                    nome=produto.nome,
                    preco_venda=preco_venda,
                    custo_medio=custo_medio,
                    margem_valor=margem_valor,
                    margem_percentual=margem_percentual,
                    quantidade_estoque=produto.quantidade_estoque,
                    quantidade_fornecedores=len(custos),
                ))

            # Menor margem percentual primeiro (o que mais precisa de atenção);
            # produtos sem custo cadastrado (sem margem calculável) vão pro final.
            itens.sort(key=lambda i: i.margem_percentual if i.margem_percentual is not None else float("inf"))
            return itens
