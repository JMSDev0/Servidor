# Processo: Criação de pedido interno (sem passar por orçamento)

Venda direta registrada por um funcionário — atendimento de balcão/telefone, ou venda pra uma empresa contratante — sem precisar de um orçamento antes. Endpoint envolvido: `POST /pedido/internal`.

## Diagrama de atividades

```mermaid
flowchart TD
    Start([Início]) --> P1[Funcionário registra venda:<br/>forma_pagamento, cliente OU<br/>empresa_contrato, itens, endereço]
    P1 --> P2["POST /pedido/internal<br/>(require_funcionario)"]

    P2 --> V1{Pedido tem<br/>pelo menos 1 item?}
    V1 -- Não --> V1E[Erro: pedido deve<br/>ter ao menos um item]
    V1 -- Sim --> V2{Tem id_cliente OU<br/>id_empresa_contrato?}
    V2 -- Não --> V2E[Erro: pedido precisa de<br/>cliente ou empresa]
    V2 -- Sim --> End1

    subgraph End1["Resolução do endereço de entrega"]
        E1{Veio id_endereco_entrega?}
        E1 -- Sim --> E2[Busca endereço cadastrado<br/>do cliente e monta texto]
        E2 --> E3{Endereço encontrado?}
        E3 -- Não --> E3E[Erro: endereço não encontrado]
        E1 -- "Não" --> E4{Veio endereco_entrega_texto?}
        E4 -- Não --> E4E[Erro: informe endereço<br/>ou endereço em texto]
    end

    E3 -- Sim --> Loop
    E4 -- Sim --> Loop

    subgraph Loop["Para cada item do pedido"]
        I1[Busca produto pelo id] --> I2{Produto existe e tem<br/>estoque suficiente?}
        I2 -- Não --> I2E[Erro: produto não encontrado<br/>ou estoque insuficiente]
        I2 -- Sim --> I3[preco_unitario = produto.preco<br/>subtotal = preco x quantidade]
        I3 --> I4[Salva item_pedido<br/>preço travado]
        I4 --> I5[Registra movimentação de<br/>estoque SAÍDA para o produto]
        I5 --> I6[Soma no valor_total do pedido]
    end

    Loop --> Fim[pedido.valor_total = soma dos itens]
    Fim --> End([Pedido criado, status inicial<br/>e estoque já debitado])
```

## Walkthrough passo a passo

**1. Registro pelo funcionário**
Só existe o caminho interno hoje (`POST /pedido/internal`, exige token de funcionário). O funcionário informa forma de pagamento, o vínculo do pedido (`id_cliente` **ou** `id_empresa_contrato` — nunca os dois vazios), a lista de itens (produto + quantidade) e o endereço de entrega.

**2. Validações antes de tocar no banco**
O pedido precisa ter pelo menos 1 item, e precisa estar vinculado a um cliente ou a uma empresa contratante — sem isso, a criação nem chega a abrir a transação.

**3. Resolução do endereço**
Mesma lógica usada quando um orçamento é aprovado (ver processo de Orçamento): se vier um `id_endereco_entrega`, o sistema busca o endereço cadastrado do cliente e monta um texto formatado (`logradouro, número, bairro, cidade - estado, CEP`); se não vier, usa direto o `endereco_entrega_texto` enviado. Uma venda pra empresa contratante normalmente cai nesse segundo caso, porque empresa não tem `endereco_cliente` cadastrado.

**4. Criação dos itens, um por um**
Para cada item: busca o produto, confere se existe e se tem `quantidade_estoque` suficiente pra atender a quantidade pedida. Se passar, trava o `preco_unitario` no valor de catálogo do produto no momento da venda (preço não muda depois, mesmo que o produto mude de preço no catálogo no futuro) e calcula o `subtotal`. Em seguida registra uma movimentação de estoque de **saída** — é esse registro que efetivamente reduz o `quantidade_estoque` do produto, não uma atualização direta.

**5. Fechamento**
O `valor_total` do pedido é a soma dos subtotais de todos os itens processados no passo 4.

## Observações / limitações conhecidas

- Não existe rota self-service pra cliente fechar o próprio pedido direto (sem passar por orçamento) — hoje a única forma de um cliente self-service gerar um `Pedido` é pelo fluxo de orçamento aprovado (ver `processo-orcamento-ate-pedido.md`). O `PedidoService.save()` já tem um parâmetro `internal=False` pensado pra isso, mas não tem rota exposta ainda, e depende de trocar a checagem de permissão de cliente (hoje ainda usa `check_user_permission`, que rejeita token de cliente) pelo mesmo `get_current_cliente` já usado em outros fluxos.
- `PedidoService.update_status` (mudar status pendente → pago → em_separação → ... → entregue/cancelado) existe no service, mas não tem rota exposta em `pedido_routes.py` ainda.
- Cancelar um pedido deveria devolver a quantidade ao estoque (movimentação de entrada) — essa regra está descrita em `documentacao/requisitos_por_entidade.md` (`RN-PED-03`), mas ainda não está implementada no `update_status`.
