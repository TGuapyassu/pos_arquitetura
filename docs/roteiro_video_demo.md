# Roteiro — vídeo demonstrativo (até 15 minutos)

Guia para gravar o vídeo exigido na entrega. Publique no **YouTube** ou **Vimeo** (público ou **não listado**) e cole o link na seção **Vídeo demonstrativo** do [`README.md`](../README.md).

**Ambiente de produção (referência):** [https://pos-arquitetura.tguapyassu.com/](https://pos-arquitetura.tguapyassu.com/)

---

## Preparação (antes de gravar)

1. Instale um gravador de tela:
   - **Windows:** [OBS Studio](https://obsproject.com/) (recomendado) ou Xbox Game Bar (`Win + G`)
   - **Linux/WSL:** OBS Studio no Windows host (mais estável) ou `gnome-screenshot` / OBS no desktop Linux
2. Abra de antemão (em abas/janelas separadas):
   - Terminal na raiz do projeto (`aula-1/`)
   - Navegador com [https://pos-arquitetura.tguapyassu.com/](https://pos-arquitetura.tguapyassu.com/)
   - Swagger local: http://localhost:8000/docs (após subir a API)
   - GitHub → Actions do repositório (um run bem-sucedido ou pronto para disparar)
   - (Opcional) Postman com a collection em `docs/postman/`
3. Narrar em **português**, com fonte/terminal legível (zoom 125–150%).
4. **Não mostre** senhas, tokens ou conteúdo de secrets (kubeconfig, `JWT_SECRET`, etc.).

---

## Timeline sugerida (≤ 15 min)

| Tempo | Bloco | O que mostrar |
|-------|-------|----------------|
| 0:00–1:00 | Abertura | Repo, objetivos da fase, URL de produção |
| 1:00–4:00 | Deploy | Compose **ou** Terraform + K8s |
| 4:00–7:00 | CI/CD | GitHub Actions (test → build → deploy) |
| 7:00–11:00 | APIs | Produção e/ou Swagger/Postman |
| 11:00–14:00 | Escalabilidade | HPA + carga ou várias OS |
| 14:00–15:00 | Encerramento | Resumo + links do README |

---

## Bloco 1 — Abertura (≈ 1 min)

Fale e mostre:

- Nome do projeto: API de Oficina Mecânica — Fase 3 (Infraestrutura).
- Objetivos: Docker, Kubernetes (`k8s/`), Terraform (`infra/`), CI/CD (GitHub Actions).
- URL de produção: https://pos-arquitetura.tguapyassu.com/
- Estrutura rápida no editor: pastas `k8s/`, `infra/`, `.github/workflows/`.

---

## Bloco 2 — Deploy (≈ 3 min)

Escolha **um** dos caminhos (não precisa dos dois).

### Opção A — Docker Compose (mais simples)

```bash
cd aula-1   # ou raiz do repo
export JWT_SECRET="$(openssl rand -hex 32)"
docker compose up --build
```

Mostre:

- Build da imagem e containers `db` + `api` healthy.
- `curl http://localhost:8000/health` → `{"status":"ok"}`.

### Opção B — Terraform + Kubernetes (mais alinhado à entrega)

```bash
cd infra/environments/local
terraform init && terraform apply
export KUBECONFIG="$(terraform output -raw kubeconfig_path)"
kubectl get nodes
kubectl get pods -n oficina

# Na raiz do projeto
docker build -t oficina-api:latest .
kind load docker-image oficina-api:latest --name oficina
export IMAGE=oficina-api:latest
export SKIP_PLATFORM=true
export JWT_SECRET="demo-somente-video"
export WEBHOOK_API_KEY="demo-webhook"
bash scripts/k8s-deploy.sh
kubectl get pods,svc,hpa -n oficina
```

Mostre pods `postgres` e `oficina-api` em `Running` / Job de migration concluído.

---

## Bloco 3 — CI/CD (≈ 3 min)

No GitHub do repositório:

1. Abra **Actions** → workflow **CI/CD**.
2. Mostre um run com jobs: **Build e testes** → **Build e push da imagem** → **Deploy Kubernetes** (na `main`).
3. Se fizer ao vivo: um commit pequeno ou push na `main` e acompanhe o pipeline.
4. Comente sem abrir valores: secrets `KUBECONFIG_DATA`, `JWT_SECRET`, `WEBHOOK_API_KEY`.
5. Aponte o arquivo [`.github/workflows/ci-cd.yml`](../.github/workflows/ci-cd.yml).

---

## Bloco 4 — Consumo das APIs (≈ 4 min)

Combine **produção** e **API local/Swagger**:

### 4.1 Produção (UI)

- Abra https://pos-arquitetura.tguapyassu.com/
- Navegue em login / listagem / criação de OS (conforme telas disponíveis).
- Diga que o front consome a API documentada no projeto.

### 4.2 Swagger ou Postman (contrato da API)

Com a API no ar (`docker compose` ou port-forward K8s):

1. http://localhost:8000/docs — Try it out:
   - `POST /auth/login`
   - `POST /clientes` (ou listar)
   - `POST /os` → `GET /os`
   - `GET /public/ordens-servico/{id}/status`
2. Ou Postman: importe `docs/postman/oficina-api.postman_collection.json` e rode Auth → OS → Público.

### Exemplos curl (narrar e colar no terminal)

```bash
# Health
curl -s http://localhost:8000/health

# Login (ajuste e-mail/senha do seed)
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@oficina.local","senha":"sua_senha"}' | jq -r .access_token)

# Listar OS ativas
curl -s http://localhost:8000/os -H "Authorization: Bearer $TOKEN"
```

---

## Bloco 5 — Escalabilidade automática (≈ 3 min)

Com cluster Kubernetes e HPA ativos:

```bash
# Ver HPA (min 2 / max 10 — ver k8s/hpa.yaml)
kubectl get hpa -n oficina
kubectl get pods -n oficina -l app=oficina-api

# Terminal 1: observar réplicas
kubectl get hpa -n oficina -w

# Terminal 2: gerar carga no /health (ajuste o host do port-forward)
kubectl port-forward svc/oficina-api 8080:80 -n oficina &
# Em outro shell — loop simples (ou use hey/ab se instalado)
for i in $(seq 1 500); do curl -s http://127.0.0.1:8080/health >/dev/null; done
```

Alternativa se a carga não subir o HPA a tempo: criar **várias ordens de serviço** via API/UI e mostrar múltiplos pods / réplicas atuais + explicar o HPA (CPU 70% / memória 80%).

```bash
kubectl describe hpa -n oficina
kubectl get deploy oficina-api -n oficina
```

---

## Bloco 6 — Encerramento (≈ 1 min)

Resuma:

- Deploy: Docker Compose e/ou Terraform (`infra/`) + manifestos (`k8s/`).
- CI/CD: GitHub Actions → testes, imagem GHCR, deploy.
- APIs: produção + Swagger/Postman.
- Escalabilidade: HPA no namespace `oficina`.

Apontar o README com links de produção, collection e este roteiro.

---

## Publicação

1. Exporte o vídeo (mp4).
2. Upload no YouTube → visibilidade **Não listado** (ou público).
3. Cole a URL no [`README.md`](../README.md), seção **Vídeo demonstrativo**, no lugar de `_inserir URL YouTube/Vimeo após publicar_`.

---

## Checklist rápido (antes de enviar a entrega)

- [ ] Vídeo ≤ 15 minutos
- [ ] Mostra deploy
- [ ] Mostra CI/CD
- [ ] Mostra consumo de APIs (e/ou UI em produção)
- [ ] Mostra ou explica escalabilidade (HPA / múltiplas OS)
- [ ] Link no README
- [ ] Nenhum secret/senha real na tela
