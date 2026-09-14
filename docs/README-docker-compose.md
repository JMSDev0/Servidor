# Tutorial básico: rodar o projeto com Docker Compose

Este guia explica como clonar o repositório e subir o projeto usando Docker Compose.

## 1. Pré-requisitos

Tenha instalados:
- Docker
- Docker Compose

Verifique a instalação:

```bash
docker --version
docker compose version
```

### Exemplo simples de um arquivo Compose

Se você estiver criando o arquivo pela primeira vez, uma estrutura mínima pode parecer assim:

```yaml
services:
  api:
    build: ./backend
    command: >
      sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8080"
    ports:
      - "8080:8080"
    environment:
      - DB_URL=url
```

Esse exemplo mostra a ideia principal: o Compose define os serviços da aplicação e mapeia as portas que serão expostas.

## 2. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd <nome-do-repositorio>
```

## 3. Subir os containers

Na raiz do projeto, execute:

```bash
docker compose up -d --build
```

Esse comando irá:
- construir a imagem da API;
- subir o banco PostgreSQL;
- rodar as migrações do Alembic;
- iniciar a API.

## 4. Verificar se os containers estão rodando

```bash
docker compose ps
```

## 5. Verificar logs

Para ver os logs da API:

```bash
docker compose logs api
```

Para ver os logs do banco:

```bash
docker compose logs db-acmoveis
```

## 6. Rodar as migrações manualmente

Se quiser rodar só as migrações manualmente:

```bash
docker compose exec api alembic upgrade head
```

## 7. Acessar a aplicação

A API deve ficar disponível em:

```text
http://localhost:8080
```

## 8. Parar os containers

```bash
docker compose down
```

## 9. Reiniciar os containers

```bash
docker compose restart
```

## 10. Dicas

- Se mudar alguma dependência no arquivo requirements.txt, reconstruir a imagem:

```bash
docker compose up -d --build
```

- Se quiser limpar volumes e containers antigos:

```bash
docker compose down -v
```
