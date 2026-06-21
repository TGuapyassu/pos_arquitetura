# Collection Postman — Oficina API

## Importar

1. Abra o [Postman](https://www.postman.com/downloads/).
2. **Import** → selecione [`oficina-api.postman_collection.json`](oficina-api.postman_collection.json).
3. Ajuste as variáveis da collection (aba **Variables**):

| Variável | Valor padrão | Descrição |
|----------|--------------|-----------|
| `baseUrl` | `http://localhost:8000` | URL base da API |
| `token` | (vazio) | Preenchido automaticamente após **Login** |
| `webhookKey` | `dev-webhook-key` | Chave para rotas `/integrations/*` |
| `osId` | `1` | ID da OS nos exemplos |

## Fluxo sugerido

1. Suba a API (`docker compose up` ou `uvicorn`).
2. Execute **Auth → Login** (requer usuário admin seedado).
3. Use as demais pastas — rotas admin usam `Bearer {{token}}`.
4. Rotas de **Integrações** usam header `X-Webhook-Key`.

## Swagger (alternativa)

Documentação interativa OpenAPI: **http://localhost:8000/docs**

ReDoc: **http://localhost:8000/redoc**
