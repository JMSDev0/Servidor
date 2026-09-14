# Tutorial básico: rodar o projeto sem Docker Compose

Este guia mostra como rodar a aplicação localmente sem usar Docker Compose.

## 1. Pré-requisitos

Tenha instalados:
- Python 3.12
- PostgreSQL
- pip

## 2. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd <nome-do-repositorio>/backend
```

## 3. Criar ambiente virtual

No diretório backend, crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente:

No Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

No Linux/macOS:

```bash
source .venv/bin/activate
```

## 4. Instalar dependências

```bash
pip install -r requirements.txt
```

## 5. Configurar o PostgreSQL

Crie um banco PostgreSQL e um usuário, por exemplo:

```sql
CREATE DATABASE acmoveis;
CREATE USER admin WITH PASSWORD '123';
ALTER ROLE admin SET client_encoding TO 'utf8';
ALTER ROLE admin SET default_transaction_isolation TO 'read committed';
ALTER ROLE admin SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE acmoveis TO admin;
```

## 6. Configurar a variável de ambiente

Crie um arquivo `.env` no diretório backend com o conteúdo:

```env
DB_URL=postgresql+psycopg://admin:123@localhost:5432/acmoveis
```

## 7. Rodar as migrações

```bash
alembic upgrade head
```

## 8. Rodar a aplicação

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

A API ficará disponível em:

```text
http://localhost:8080
```

## 9. Parar a aplicação

Pressione:

```text
Ctrl + C
```

## 10. Dicas

- Se quiser verificar se o banco está acessível, use:

```bash
psql -U admin -d acmoveis -h localhost
```

- Se alguma dependência mudar, reinstale com:

```bash
pip install -r requirements.txt
```
