# Testes

Guia completo (conceitos + explicação do código, pra quem nunca escreveu teste):
[`docs/README-testes.md`](../docs/README-testes.md).

## Como rodar

```bash
# de dentro de backend/, com o venv ativado
pip install -r requirements-dev.txt   # só na primeira vez (adiciona pytest e httpx)
python -m pytest -v                   # roda todos os testes, mostrando o nome de cada um
```

Outros comandos úteis:

```bash
python -m pytest tests/test_produto_service.py   # só um arquivo
python -m pytest -k "senha_errada"                # só testes com esse nome
```

Não precisa de Postgres rodando: os testes usam um banco SQLite que existe só na
memória, criado do zero antes de cada teste (ver `tests/conftest.py`).

## Arquivos

- `conftest.py` — o "setup" dos testes: troca o banco por SQLite em memória e
  disponibiliza `client` (pra chamar rotas HTTP) e `db_session` (pra inserir dados
  direto no banco) pra qualquer teste que precisar.
- `helpers.py` — funções simples pra criar um funcionário/categoria de teste. Não é
  fixture, é só função Python normal, chamada explicitamente em cada teste.
- `test_produto_service.py` — testes **unitários**: chamam `ProdutoService` direto em
  Python, sem passar por HTTP. Testam regra de negócio (validação, permissão).
- `test_produto_api.py` — testes de **integração**: chamam as rotas HTTP de verdade
  (`client.post("/produto/internal", ...)`), cobrindo rota + service + banco juntos.
- `test_auth.py` — login: mistura os dois tipos, pra dar pra comparar.
