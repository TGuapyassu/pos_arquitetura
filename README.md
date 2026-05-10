# API de Oficina Mecânica (MVP)

Back-end monolítico em **Python** com **FastAPI**, **SQLAlchemy 2**, **PostgreSQL** e **Alembic**, organizado com **Domain-Driven Design (DDD)** e arquitetura em camadas. O sistema modela **clientes**, **veículos**, **serviços**, **peças/estoque** e **ordens de serviço (OS)**, com autenticação **JWT**, rotas administrativas e consulta pública de OS.

---

## Objetivos

1. **Gestão de oficina**  
   Centralizar cadastro de clientes e veículos, tabela de serviços e peças, e o ciclo de vida de ordens de serviço (diagnóstico, aprovação, execução, finalização e entrega).

2. **Regras de negócio no domínio**  
   Manter regras (máquina de estados da OS, cálculo de orçamento, controle de estoque) fora de controllers e fora de “regra escondida” no ORM, alinhado a DDD e boas práticas.

3. **API REST clara e documentada**  
   Expor contratos previsíveis, com **Swagger (OpenAPI)** automático, para integração com front-ends, apps ou automações.

4. **Operação e evolução**  
   Facilitar execução local e em contêiner, migrations versionadas, testes automatizados e base para crescer (mais agregados, filas, relatórios) sem reescrever o núcleo.

5. **Segurança básica**  
   Separar rotas que exigem administrador (JWT) da consulta pública de status de OS (sem autenticação, com escopo de dados reduzido).

---

## O que o sistema oferece (escopo do MVP)

| Área | Descrição |
|------|-----------|
| **Clientes** | CPF/CNPJ validado, nome e contato; CRUD protegido. |
| **Veículos** | Placa (padrão antigo ou Mercosul), marca, modelo, ano, vinculados a cliente; CRUD protegido. |
| **Serviços** | Nome e preço; catálogo usado em itens da OS; CRUD protegido. |
| **Peças** | Nome, preço e quantidade em estoque; CRUD e ajuste de estoque; baixa automática ao compor a OS. |
| **Ordens de serviço** | Criação com itens (serviços e peças), status com validação, aprovação explícita antes da execução, valor total calculado. |
| **Público** | Leitura de resumo de OS (status e totais) sem token. |
| **Admin** | Usuário com `is_admin` e JWT para CRUDs e mutações de OS. |

---

## Stack técnica

- **Python** 3.11+
- **FastAPI** — API HTTP e documentação OpenAPI
- **Pydantic v2** — DTOs e validação de entrada
- **SQLAlchemy 2** — persistência
- **PostgreSQL** — banco principal (testes podem usar SQLite em memória)
- **Alembic** — migrations
- **python-jose** + **passlib/bcrypt** — JWT e hash de senha
- **pytest** + **pytest-cov** — testes; cobertura mínima **80%** em `app/domain` e `app/application`
- **Docker** — API + Postgres (opcional)

---

## Arquitetura (camadas)

```
app/
├── domain/              # Núcleo: entidades, VOs, enums, políticas, interfaces de repositório
├── application/         # Casos de uso, DTOs, mapeamento para respostas
├── infrastructure/      # ORM, repositórios concretos, config, JWT, conexão
└── presentation/        # Rotas FastAPI, dependências (auth), mapeamento exceção → HTTP
```

| Camada | Responsabilidade |
|--------|------------------|
| **Domain** | Regras invariantes: transições de status da OS, cálculo de totais, estoque não negativo, value objects (CPF/CNPJ, placa, etc.). |
| **Application** | Orquestra repositórios e entidades: um caso de uso por fluxo (criar OS, aprovar, listar, etc.). |
| **Infrastructure** | Detalhes técnicos: tabelas SQLAlchemy, implementação dos repositórios, assinatura JWT, leitura de `Settings`. |
| **Presentation** | HTTP: roteamento, `Depends` de sessão e JWT, conversão de exceções de domínio em 4xx/5xx. |

**Princípios adotados:** regras de negócio não ficam no controller; o ORM não concentra cálculo de orçamento nem máquina de estados; dependências apontam para abstrações (repositórios) na infraestrutura.

---

## Regras de negócio (Ordem de Serviço)

**Status possíveis:** `RECEBIDA` → `EM_DIAGNOSTICO` → `AGUARDANDO_APROVACAO` → `EM_EXECUCAO` → `FINALIZADA` → `ENTREGUE`.

- A transição de `AGUARDANDO_APROVACAO` para `EM_EXECUCAO` **não** é feita por `PATCH /os/{id}/status` — use **`POST /os/{id}/aprovar`** (aprovação explícita do orçamento).
- O **valor total** da OS é derivado dos itens (serviços e peças com preço de referência na hora do vínculo).
- Ao **incluir peças** na criação da OS, o estoque é **baixado**; não é permitido estoque **negativo**.
- Datas: criação/atualização automáticas; finalização e entrega registradas ao atingir `FINALIZADA` e `ENTREGUE`, conforme implementado no domínio.

---

## Pré-requisitos

- **Python** 3.11 ou superior  
- **PostgreSQL** 14+ (recomendado) para ambiente de desenvolvimento com dados reais  
- **Docker** e **Docker Compose** (opcional, para subir API + banco com um comando)

Ferramentas de linha de comando: `git`, `curl` (para testar a API), opcionalmente `psql` para inspecionar o banco.

---

## Instalação (desenvolvimento local)

### 1. Clonar e ambiente virtual

```bash
git clone <url-do-repositório> oficina-api
cd oficina-api
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e ".[dev]"
```

### 2. Variáveis de ambiente

```bash
cp .env.example .env
```

Edite `.env` e ajuste no mínimo:

| Variável | Descrição |
|----------|-----------|
| `DATABASE_URL` | URL SQLAlchemy, ex.: `postgresql+psycopg2://usuario:senha@localhost:5432/oficina` |
| `JWT_SECRET` | Segredo forte (nunca commitar o valor real). |
| `JWT_ALGORITHM` | Padrão `HS256`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do access token. |
| `CORS_ORIGINS` | `*` ou origens separadas por vírgula. |
| `APP_ENV` | `development` ou `production` (influencia criação de schema em dev). |

### 3. Banco de dados e migrations

Crie o banco no PostgreSQL (ex.: banco `oficina` e usuário com permissão). Depois:

```bash
export DATABASE_URL="postgresql+psycopg2://oficina:oficina@localhost:5432/oficina"
alembic upgrade head
```

### 4. Usuário administrador (seed)

```bash
export DATABASE_URL="postgresql+psycopg2://oficina:oficina@localhost:5432/oficina"
export JWT_SECRET="mesmo-segredo-usado-na-app"   # se o script carregar config
export ADMIN_EMAIL="admin@oficina.local"
export ADMIN_SENHA="sua_senha_segura"
python3 scripts/seed_admin.py
```

> Em SQLite (apenas testes/seed local), o script pode criar tabelas; em produção use **sempre** `alembic upgrade head` antes do seed e da API.

### 5. Subir a API

```bash
export DATABASE_URL="postgresql+psycopg2://..."
export JWT_SECRET="seu-segredo"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Swagger UI:** http://localhost:8000/docs  
- **ReDoc:** http://localhost:8000/redoc  
- **Health:** `GET /health` → `{"status":"ok"}`

---

## Uso com Docker Compose

Cria o serviço `db` (Postgres) e a `api` (build do `Dockerfile`), executa migrations e inicia o Uvicorn.

```bash
export JWT_SECRET="$(openssl rand -hex 32)"   # Linux/macOS; no Windows, defina manualmente
docker compose up --build
```

- API: **http://localhost:8000**  
- Depois de subir, execute o **seed do admin** (a partir do host, apontando para o mesmo `DATABASE_URL` do compose) ou crie o usuário por script/SQL, conforme sua preferência de deploy.

Arquivo `docker-compose.yml`: usuário, senha e banco padrão `oficina`; ajuste credenciais em produção e use segredos externos (não versionar produção com senhas padrão).

---

## Autenticação e autorização

1. **Login** — `POST /auth/login` com `email` e `senha` (usuário com `is_active` e, para administrativo, `is_admin`). Resposta: `access_token` (Bearer JWT).  
2. **Rotas administrativas** — header `Authorization: Bearer <access_token>`. O backend valida o token e exige `is_admin` onde as rotas estiverem protegidas com essa regra.  
3. **Consulta pública** — `GET /public/ordens-servico/{id}` **sem** token: retorno limitado a campos de acompanhamento (status, valores, datas de entrega/finalização).

Em produção: HTTPS obrigatório, `JWT_SECRET` longo e rotativo, senhas fortes no seed e política de CORS restrita.

---

## Resumo da API (REST)

| Método | Rota | Autenticação | Descrição |
|--------|------|--------------|------------|
| `POST` | `/auth/login` | Não | Obtém JWT. |
| `GET` | `/health` | Não | Saúde da aplicação. |
| `GET` | `/public/ordens-servico/{id}` | Não | Consulta pública da OS. |
| `POST` | `/os` | Admin (JWT) | Cria OS com itens. |
| `GET` | `/os` | Admin | Lista OS. |
| `GET` | `/os/{id}` | Admin | Detalhe da OS. |
| `PATCH` | `/os/{id}/status` | Admin | Muda status (máquina de estados). |
| `POST` | `/os/{id}/aprovar` | Admin | Aprova orçamento → execução. |
| | `/clientes`, `/veiculos`, `/servicos`, `/pecas` | Admin | CRUDs conforme rotas expostas no OpenAPI. |
| `PATCH` | `/pecas/{id}/estoque` | Admin | Ajusta estoque (absoluto ou delta). |

A lista exata e os corpos de requisição estão em **`/docs`** (schemas gerados a partir dos DTOs).

---

## Exemplos de uso (curl)

### 1) Login e token

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@oficina.local","senha":"sua_senha"}' | jq -r .access_token)

echo "Token: ${TOKEN:0:20}..."
```

(Sem `jq`, copie o `access_token` manualmente da resposta JSON.)

### 2) Criar cliente, veículo, serviço e peça (ordem mínima para uma OS)

Substitua `<TOKEN>` e ids conforme as respostas anteriores.

```bash
H="Authorization: Bearer <TOKEN>"

# Cliente
curl -s -X POST http://localhost:8000/clientes -H "$H" -H "Content-Type: application/json" \
  -d '{"nome":"Maria Souza","contato":"(11)90000-0000","cpf_cnpj":"52998224725"}'

# Veículo (cliente_id = id retornado)
curl -s -X POST http://localhost:8000/veiculos -H "$H" -H "Content-Type: application/json" \
  -d '{"cliente_id":1,"placa":"ABC1D23","marca":"Fiat","modelo":"Argo","ano":2019}'

# Serviço
curl -s -X POST http://localhost:8000/servicos -H "$H" -H "Content-Type: application/json" \
  -d '{"nome":"Troca de óleo","preco":"150.00"}'

# Peça
curl -s -X POST http://localhost:8000/pecas -H "$H" -H "Content-Type: application/json" \
  -d '{"nome":"Filtro de óleo","preco":"45.00","quantidade_estoque":10}'
```

### 3) Criar OS com serviço e peça

```bash
curl -s -X POST http://localhost:8000/os -H "$H" -H "Content-Type: application/json" \
  -d '{
    "cliente_id": 1,
    "veiculo_id": 1,
    "servicos": [{"servico_id": 1, "quantidade": 1}],
    "pecas": [{"peca_id": 1, "quantidade": 2}]
  }'
```

### 4) Acompanhar transição: diagnóstico → aguardando aprovação → aprovar → finalizar (exemplo)

Ajuste `OS_ID` e corpos conforme as respostas da API.

```bash
OS_ID=1

curl -s -X PATCH "http://localhost:8000/os/${OS_ID}/status" -H "$H" -H "Content-Type: application/json" \
  -d '{"status":"EM_DIAGNOSTICO"}'

curl -s -X PATCH "http://localhost:8000/os/${OS_ID}/status" -H "$H" -H "Content-Type: application/json" \
  -d '{"status":"AGUARDANDO_APROVACAO"}'

curl -s -X POST "http://localhost:8000/os/${OS_ID}/aprovar" -H "$H"

curl -s -X PATCH "http://localhost:8000/os/${OS_ID}/status" -H "$H" -H "Content-Type: application/json" \
  -d '{"status":"FINALIZADA"}'

curl -s -X PATCH "http://localhost:8000/os/${OS_ID}/status" -H "$H" -H "Content-Type: application/json" \
  -d '{"status":"ENTREGUE"}'
```

### 5) Consulta pública (cliente, sem token)

```bash
curl -s "http://localhost:8000/public/ordens-servico/1"
```

### 6) Ajuste de estoque (admin)

```bash
# Define estoque absoluto = 5
curl -s -X PATCH "http://localhost:8000/pecas/1/estoque" -H "$H" -H "Content-Type: application/json" \
  -d '{"quantidade":5,"ajuste_absoluto":true}'

# Soma -2 ao estoque atual
curl -s -X PATCH "http://localhost:8000/pecas/1/estoque" -H "$H" -H "Content-Type: application/json" \
  -d '{"quantidade":-2,"ajuste_absoluto":false}'
```

---

## Testes automáticos

```bash
source .venv/bin/activate
pytest
```

Os testes cobrem **domínio** (políticas de status, value objects, entidades), **casos de uso** e **integração HTTP** (FastAPI com SQLite em memória), em `tests/`.

### Cobertura mínima de 80% (domínios críticos)

Para o MVP, **domínios críticos** são o núcleo de negócio versionado em:

| Pacote | Conteúdo |
|--------|-----------|
| `app/domain` | Entidades, value objects, enums, serviços de domínio e políticas (ex.: máquina de estados da OS). Interfaces em `app/domain/repositories/` são contratos e ficam **fora** do cálculo. |
| `app/application` | Casos de uso, DTOs e mapeamentos que orquestram o domínio. |

O `pytest` está configurado no `pyproject.toml` para medir **`app/domain`** + **`app/application`** com falha se a cobertura global desses pacotes for **inferior a 80%** (`--cov-fail-under=80`).

Relatório HTML só desses pacotes:

```bash
pytest --cov=app/domain --cov=app/application --cov-report=html
# Abrir htmlcov/index.html
```

Para uma visão opcional de todo o pacote `app` (incluindo infraestrutura e rotas), sem alterar o critério de falha do CI local:

```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=0
```

---

## Relatório de análise de vulnerabilidades

Foi elaborado um relatório com **resultados reais de scan** (Bandit no código-fonte e pip-audit nas dependências) e **análise interpretativa**:

| Ficheiro | Descrição |
|----------|-----------|
| `docs/relatorio_analise_vulnerabilidades.md` | Relatório completo em Markdown (versionável). |
| `docs/relatorio_analise_vulnerabilidades.pdf` | Versão PDF (regenerável). |

**Gerar novamente o PDF** (requer `fpdf2` e, no Linux/WSL, fontes tipo DejaVu):

```bash
pip install fpdf2
python3 scripts/gerar_relatorio_vulnerabilidades_pdf.py
```

**Documentação DDD (Event Storming, diagramas, linguagem ubíqua):** `docs/ddd_documentacao_event_storming.md` (versão para entrega: `docs/ddd_documentacao_entrega.md`) — use no **Miro** (colar Mermaid de [mermaid.live](https://mermaid.live) como imagem) ou em **FigJam** / **Notion**.

**Repetir os scans** descritos no relatório:

```bash
bandit -r app -f txt
pip freeze | pip-audit --requirement /dev/stdin
```

---

## Resolução de problemas (FAQ)

| Sintoma | Verificação |
|--------|--------------|
| Erro de conexão com o banco | `DATABASE_URL` acessível do processo; Postgres escutando; firewall. |
| `alembic` não acha tabelas | `DATABASE_URL` no mesmo banco; rodar `alembic upgrade head` antes da API. |
| `401` / `403` | Token no header; usuário com `is_admin` nas rotas administrativas. |
| `400` em mudança de status | Respeitar a máquina de estados; não ir de `AGUARDANDO_APROVACAO` a `EM_EXECUCAO` só com PATCH — use `POST /aprovar`. |
| `409` em criação de OS com peças | Estoque insuficiente para a quantidade solicitada. |
| Aviso do `passlib`/`bcrypt` | O projeto fixa range de `bcrypt` compatível; em ambiente novo, use `pip install -e ".[dev]"` conforme `pyproject.toml`. |

---

## Estrutura de pastas (referência)

```
.
├── app/
│   ├── main.py                 # Fábrica da aplicação FastAPI, CORS, lifespan, handlers
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── presentation/
├── alembic/                    # Migrations
├── docs/                       # Vulnerabilidades, DDD (Event Storming, Mermaid)
├── scripts/
│   ├── seed_admin.py           # Criação do usuário admin
│   └── gerar_relatorio_vulnerabilidades_pdf.py
├── tests/
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── README.md
```

