# Deploy Kubernetes — Oficina API

Manifestos para deploy da API e **PostgreSQL interno** no namespace `oficina`. O banco roda como StatefulSet com PVC persistente; a API conecta via Service `postgres:5432`.

```text
namespace oficina
├── StatefulSet postgres  ──► PVC postgres-data
├── Service postgres:5432
├── Job migration         ──► postgres
├── Deployment oficina-api ──► postgres
├── Service oficina-api:80
└── HPA
```

## Pré-requisitos

- Cluster Kubernetes (minikube, kind, EKS, GKE, AKS, etc.)
- `kubectl` configurado
- Imagem Docker construída localmente ou publicada em registry:

```bash
docker build -t oficina-api:latest .
# kind/minikube local:
kind load docker-image oficina-api:latest
# ou: minikube image load oficina-api:latest
```

- **metrics-server** instalado (obrigatório para HPA):

```bash
# minikube
minikube addons enable metrics-server

# kind / cluster genérico
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

## Estrutura dos manifestos

| Arquivo | Recurso | Descrição |
|---------|---------|-----------|
| `namespace.yaml` | Namespace | Isola recursos em `oficina` |
| `postgres.yaml` | Secret, PVC, StatefulSet, Service | PostgreSQL 16 interno (`postgres:5432`) |
| `configmap.yaml` | ConfigMap | Variáveis não sensíveis da API |
| `secret.example.yaml` | Secret (template) | `DATABASE_URL` apontando para `postgres:5432` |
| `migration-job.yaml` | Job | `alembic upgrade head` (initContainer aguarda Postgres) |
| `deployment.yaml` | Deployment | API (2 réplicas, probes, initContainer wait-for-postgres) |
| `service.yaml` | Service | ClusterIP porta 80 → 8000 |
| `hpa.yaml` | HorizontalPodAutoscaler | CPU 70%, memória 80%, min 2 / max 10 |

## ConfigMap vs Secret

| ConfigMap (`oficina-api-config`) | Secret (`oficina-secrets`) |
|----------------------------------|----------------------------|
| `APP_ENV`, `CORS_ORIGINS`, `JWT_ALGORITHM` | `DATABASE_URL` → `postgres:5432` |
| `EMAIL_ENABLED`, `SMTP_HOST`, `SMTP_PORT`, `EMAIL_FROM` | `JWT_SECRET` |
| `RUN_MIGRATIONS=false` | `WEBHOOK_API_KEY` |
| | `SMTP_USER`, `SMTP_PASSWORD` |

Credenciais do Postgres ficam em **`postgres-secrets`** (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`) — definidas em `postgres.yaml`.

## Deploy passo a passo

```bash
# 1. Namespace e PostgreSQL interno
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres.yaml
kubectl wait --for=condition=ready pod -l app=postgres -n oficina --timeout=120s

# 2. ConfigMap e Secret da API
kubectl apply -f k8s/configmap.yaml

# Secret (escolha uma opção)
kubectl apply -f k8s/secret.example.yaml   # apenas dev/demo — troque os valores
# ou:
kubectl create secret generic oficina-secrets -n oficina \
  --from-literal=DATABASE_URL='postgresql+psycopg2://oficina:oficina@postgres:5432/oficina' \
  --from-literal=JWT_SECRET='segredo-longo' \
  --from-literal=WEBHOOK_API_KEY='chave-webhook' \
  --from-literal=SMTP_USER='' \
  --from-literal=SMTP_PASSWORD=''

# 3. Migrations (aguardar conclusão)
kubectl delete job oficina-api-migration -n oficina --ignore-not-found
kubectl apply -f k8s/migration-job.yaml
kubectl wait --for=condition=complete job/oficina-api-migration -n oficina --timeout=120s

# 4. API, Service e HPA
kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml -f k8s/hpa.yaml

# 5. Verificar
kubectl get pods,svc,hpa -n oficina
kubectl port-forward svc/oficina-api 8080:80 -n oficina
curl http://localhost:8080/health
```

> **Produção real:** troque senhas padrão (`oficina`/`oficina`) e considere backup do PVC `postgres-data`. Para entrega acadêmica ou ambiente local, as credenciais demo são aceitáveis.

## Escalabilidade (HPA)

O HPA ajusta réplicas entre **2 e 10** com base em:

- CPU média alvo: **70%**
- Memória média alvo: **80%**

As migrations **não** rodam em cada pod — apenas no Job dedicado, evitando corrida entre réplicas.

## Exposição externa

Este stack usa `ClusterIP`. Para acesso externo temporário:

```bash
kubectl port-forward svc/oficina-api 8000:80 -n oficina
```

Em produção, configure um **Ingress** ou **LoadBalancer** conforme o provedor do cluster.

## Deploy automatizado (CI/CD)

Push na branch `main` dispara o workflow [`.github/workflows/ci-cd.yml`](../.github/workflows/ci-cd.yml), que:

1. Executa `pytest` (build da aplicação + testes)
2. Publica a imagem em `ghcr.io/<owner>/oficina-api:<sha>`
3. Aplica os manifestos via [`scripts/k8s-deploy.sh`](../scripts/k8s-deploy.sh) na ordem:
   - `namespace.yaml` → `postgres.yaml` (banco) → aguarda Postgres
   - `configmap.yaml` → Secret `oficina-secrets` (GitHub Secrets)
   - Migration Job → `deployment.yaml` + `service.yaml` + `hpa.yaml`

Secrets necessários no GitHub: `KUBECONFIG_DATA`, `JWT_SECRET`, `WEBHOOK_API_KEY`, `DATABASE_URL` (opcional se usar padrão interno), `SMTP_USER` / `SMTP_PASSWORD` (opcionais).

Para deploy manual com imagem do registry:

```bash
export IMAGE="ghcr.io/<owner>/oficina-api:latest"
export JWT_SECRET="..."
export WEBHOOK_API_KEY="..."
bash scripts/k8s-deploy.sh
```

Em PRs e branches que não são `main`, o pipeline roda apenas testes e valida o build Docker (sem push nem deploy).

## Provisionamento com Terraform (`infra/`)

Para ambiente local com **kind**, use [`infra/`](../infra/) antes do deploy manual:

```bash
cd infra/environments/local
terraform init && terraform apply
export KUBECONFIG="$(terraform output -raw kubeconfig_path)"
export SKIP_PLATFORM=true
bash scripts/k8s-deploy.sh   # pula namespace/postgres já criados pelo Terraform
```

Ver [`infra/README.md`](../infra/README.md) para recursos provisionados e `terraform destroy`.
