# Testes automatizados — guia pra quem nunca escreveu um teste

Esse documento explica, com calma, o que são os testes que estão em `tests/` e
como o código deles funciona. A ideia é dar pra ler de cima a baixo e entender,
mesmo sem experiência nenhuma com testes.

## 1. O que é um "teste automatizado"

É um pedaço de código cujo único trabalho é executar outro pedaço de código e
checar se o resultado é o esperado. Em vez de você abrir o Postman, logar,
criar um produto e olhar a resposta na mão pra confirmar que "funciona", você
escreve isso uma vez como código, e toda vez que rodar esse código ele repete
o processo sozinho e te diz "passou" ou "falhou".

Vantagem principal: quando você muda uma linha em `produto_service.py`, roda
`python -m pytest` e sabe em segundos se quebrou alguma coisa que já
funcionava antes — sem precisar testar tudo na mão de novo.

## 2. Unitário vs. integração

Os dois tipos de teste que existem em `tests/` testam a mesma funcionalidade,
mas em "profundidades" diferentes:

| | Unitário | Integração |
|---|---|---|
| O que chama | a função/método Python direto | a rota HTTP, através do `client` |
| Exemplo | `produto_service.save(dados, usuario)` | `client.post("/produto/internal", json=dados)` |
| O que passa por baixo | só o service | rota → autenticação → service → repository → banco |
| Quando usar | pra testar uma regra de negócio isolada (ex: "preço negativo deve falhar") | pra testar o fluxo completo, como um front-end real usaria |
| Velocidade | mais rápido | um pouco mais lento (mas ainda é tudo em memória, não é lento de verdade) |

Nos arquivos: `test_produto_service.py` é unitário, `test_produto_api.py` é
integração. `test_auth.py` tem os dois, um em cada seção, pra comparar lado a
lado.

## 3. Vocabulário do pytest usado aqui

O framework de testes usado é o [pytest](https://docs.pytest.org/). Ele tem
algumas palavras/convenções próprias que aparecem em todo teste:

- **`test_` no nome da função**: é assim que o pytest reconhece o que é um
  teste. Qualquer função `def test_algumacoisa(): ...` dentro de um arquivo
  `test_*.py` vira um teste que roda automaticamente.
- **`assert`**: é a verificação. `assert x == y` não faz nada se for verdade;
  se for falso, o teste falha e o pytest te mostra os dois valores pra
  comparar.
- **`pytest.raises(AlgumErro)`**: usado quando o comportamento *correto* é dar
  erro. `with pytest.raises(ValueError): produto_service.save(dados_invalidos, usuario)`
  lê-se como "eu espero que essa chamada solte um `ValueError`". Se não soltar
  nenhum erro, o teste falha (porque o comportamento esperado não aconteceu).
- **fixture**: uma função marcada com `@pytest.fixture`, definida em
  `conftest.py`. Quando um teste tem, por exemplo, `client` como parâmetro:

  ```python
  def test_algumacoisa(client):
      resposta = client.get("/produto/list")
  ```

  o pytest vê que existe uma fixture chamada `client`, chama ela, e entrega o
  resultado como esse parâmetro. É assim que `client` e `db_session` "aparecem"
  nos testes sem nenhum import — é a única parte "mágica" do pytest, o resto é
  Python normal.
- **`autouse=True`**: uma fixture que roda em *todo* teste automaticamente,
  mesmo que o teste não peça ela como parâmetro. Usada na fixture
  `banco_limpo` (explicada abaixo), pra garantir que todo teste comece com o
  banco vazio.

## 4. `tests/conftest.py` — o setup

Esse arquivo tem um nome especial: o pytest sempre carrega `conftest.py`
automaticamente antes de rodar os testes de uma pasta, e tudo que é
`@pytest.fixture` ali fica disponível pra qualquer arquivo `test_*.py` da
mesma pasta, sem precisar importar.

O que ele faz, em ordem:

1. **Define variáveis de ambiente antes de importar o app** (`DB_URL`,
   `SECRET_KEY`, `SERVER_TYPE`). Precisa ser antes porque `app/db/config.py`
   lê essas variáveis assim que é importado — se a gente importasse o app
   primeiro, ele já teria tentado conectar no Postgres de verdade.
2. **Troca o banco por SQLite em memória.** A aplicação, em produção, usa
   Postgres. Nos testes, a gente substitui `engine`/`sessionMaker` (as duas
   variáveis que `app/db/config.py` usa pra abrir conexões) por um SQLite que
   não escreve em disco nenhum, só existe enquanto os testes rodam. Isso
   evita precisar de um Postgres instalado só pra rodar os testes, e garante
   que os testes nunca mexem em dado de verdade.
3. **`banco_limpo` (fixture `autouse`)**: antes de cada teste, apaga e recria
   todas as tabelas. Isso garante que um teste nunca "veja" dado deixado por
   outro teste que rodou antes.
4. **`db_session` (fixture)**: entrega uma sessão do SQLAlchemy pronta pra
   inserir dado de teste direto nas tabelas (sem passar pelas validações do
   service — é só pra montar o cenário do teste).
5. **`client` (fixture)**: entrega um `TestClient` do FastAPI, que é como um
   navegador/Postman que já sabe conversar com a API sem precisar de rede —
   é ele que os testes de integração usam pra chamar as rotas.

## 5. `tests/helpers.py` — funções de apoio (não são fixture)

```python
def criar_funcionario(db_session, tipo=TipoFuncionario.ADMIN, senha="senha123"):
    funcionario = Funcionario(nome=..., cpf=..., senha_hash=hash_password(senha), ...)
    db_session.add(funcionario)
    db_session.commit()
    return funcionario
```

Isso aqui **não** é fixture — é só uma função Python comum. A diferença é de
propósito: uma fixture "aparece sozinha" quando pedida como parâmetro; uma
função helper você chama explicitamente dentro do teste
(`funcionario = criar_funcionario(db_session)`), o que deixa mais fácil ver,
lendo o teste, exatamente o que foi criado.

`usuario_logado(funcionario)` monta o dict `{"login": ..., "type": "administrador"}`
— é o mesmo formato que o app usa internamente pra representar "quem está
logado" depois de decodificar o token JWT. Usar esse dict direto (em vez de
gerar um token JWT de verdade) é o que torna os testes de
`test_produto_service.py` **unitários**: eles pulam a parte de
autenticação/HTTP e testam só a lógica do service.

## 6. `tests/test_produto_service.py` — exemplo comentado

```python
def test_criar_produto_sem_nome_falha(db_session):
    funcionario = criar_funcionario(db_session)
    categoria = criar_categoria(db_session)
    dados = ProdutoCreate(nome="", preco=25.0, quantidade_estoque=10, id_categoria=categoria.id_categoria)

    with pytest.raises(ValueError):
        produto_service.save(dados, usuario_logado(funcionario))
```

Lendo de cima a baixo:

1. `db_session` some como parâmetro → o pytest entrega a fixture (banco
   limpo, pronto pra usar).
2. Cria um funcionário e uma categoria direto no banco (helpers, não fixture).
3. Monta um `ProdutoCreate` com `nome=""` — dado inválido de propósito.
4. Espera que `produto_service.save(...)` dê `ValueError`. Esse é o
   comportamento real de `ProdutoService._create_validate()`
   (`app/service/produto_service.py`), que checa `if not produto.nome: raise ValueError(...)`.

Esse teste passa hoje porque o código realmente valida isso. Se um dia alguém
remover essa validação sem querer, esse teste passa a falhar — é esse o valor
de ter o teste escrito.

## 7. `tests/test_produto_api.py` — exemplo comentado

```python
def test_criar_produto_como_funcionario_logado(client, db_session):
    funcionario = criar_funcionario(db_session)
    categoria = criar_categoria(db_session)
    headers = login_e_pegar_header(client, funcionario)

    resposta = client.post("/produto/internal", json={...}, headers=headers)

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Bolo de Cenoura"
```

Diferença chave em relação ao unitário: aqui a gente **loga de verdade**
(`login_e_pegar_header` chama `POST /auth/login` de verdade e recebe um token
JWT real), e chama `POST /produto/internal` como uma requisição HTTP completa
— o FastAPI valida o corpo da requisição, decodifica o token, chama o service,
que chama o repository, que grava no banco. É o caminho inteiro, de ponta a
ponta.

## 8. O bug encontrado (e corrigido) escrevendo esses testes

Ao escrever `test_deletar_produto_como_funcionario`, o teste falhou: depois de
deletar um produto (soft delete — ele fica marcado `ativo=False`, mas não é
removido da tabela), ele continuava aparecendo em `GET /produto/list`.

Causa: `ProdutoRepository.get_all()` não filtrava por `ativo`:

```python
# antes
def get_all(self):
    return self.db.query(Produto).all()

# depois
def get_all(self):
    return self.db.query(Produto).filter(Produto.ativo == True).all()
```

(`find_paginated`, usado em `GET /produto/find`, já filtrava certo — o bug era
só em `get_all`.) Esse é um exemplo real de por que vale ter teste: ele achou
um bug de verdade num fluxo que "parecia" funcionar (a rota respondia 200 e
não dava erro nenhum — só devolvia o dado errado).

## 9. Como rodar

```bash
cd backend
.\venv\Scripts\Activate.ps1        # ativa o ambiente virtual (Windows)
pip install -r requirements-dev.txt   # só na primeira vez
python -m pytest -v                   # roda tudo, mostrando o nome de cada teste
```

Outros comandos úteis:

```bash
python -m pytest tests/test_produto_service.py     # só um arquivo
python -m pytest -k "senha_errada"                   # só testes com esse nome
python -m pytest -v --tb=short                       # erro resumido quando falha
```

Não precisa de Postgres rodando — ver seção 4.

## 10. Como adicionar um teste novo

1. Escolha o arquivo certo (ou crie um `test_<modulo>.py` novo).
2. Escreva uma função `def test_o_que_estou_testando(...):` — nomeie descrevendo
   o comportamento, não a implementação (ex: `test_criar_produto_sem_nome_falha`,
   não `test_save_1`).
3. Peça `db_session`, `client`, ou ambos como parâmetro, dependendo se o teste é
   unitário ou de integração.
4. Monte o cenário (helpers de `tests/helpers.py`, ou insira direto via
   `db_session` se precisar de algo que não tem helper ainda).
5. Chame o código que quer testar e faça os `assert`.
6. Rode só esse arquivo enquanto escreve: `python -m pytest tests/test_seu_arquivo.py -v`.
