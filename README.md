# Projeto Backend

Este repositório contém o backend da aplicação, com FastAPI, SQLAlchemy, Alembic e PostgreSQL.

## Como usar

Existem dois caminhos principais para rodar o projeto:

1. Com Docker Compose
2. Sem Docker Compose

## Opção 1: Rodar com Docker Compose

Se quiser usar o ambiente pronto com banco e API em containers, siga o tutorial:

- [docs/README-docker-compose.md](docs/README-docker-compose.md)

Para usar o fluxo com Docker Compose, basta manter o arquivo de configuração do Compose junto ao projeto e executar:

```bash
docker compose up -d --build
```

Depois, a API ficará disponível em:

```text
http://localhost:8080
```

## Opção 2: Rodar sem Docker Compose

Se quiser rodar localmente na sua máquina, siga o tutorial:

- [docs/README-sem-docker-compose.md](docs/README-sem-docker-compose.md)

Resumo rápido:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## Migrações do banco

Para aplicar as migrações:

```bash
alembic upgrade head
```

Se quiser voltar uma migração:

```bash
alembic downgrade -1
```

## Estrutura básica

- app/: código da aplicação
- app/api/: rotas da API
- app/db/: configuração do banco e migrações
- app/models/: modelos do SQLAlchemy
- docs/: tutoriais de uso

## Observações

- O projeto usa PostgreSQL.
- O arquivo de dependências está em [requirements.txt](requirements.txt).
- Se você estiver usando o fluxo com Docker Compose, o arquivo de configuração deve ficar na mesma raiz de execução do projeto, junto à pasta backend.
