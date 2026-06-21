# Terraform — Infraestrutura como Código (local)

Scripts Terraform em [`infra/`](../infra/) para provisionar **cluster Kubernetes local (kind)**, **PostgreSQL interno** e **metrics-server**, alinhados aos manifestos em [`../k8s/`](../k8s/).

## Recursos criados

| Recurso | Módulo | Descrição |
|---------|--------|-----------|
| `kind_cluster` | `kind-cluster` | Cluster Kubernetes local via Docker |
| `kubernetes_namespace` | `k8s-platform` | Namespace `oficina` |
| `kubernetes_secret` | `k8s-platform` | `postgres-secrets` (user/senha/db) |
| `kubernetes_persistent_volume_claim` | `k8s-platform` | PVC `postgres-data` (1Gi) |
| `kubernetes_stateful_set` | `k8s-platform` | PostgreSQL 16 (`postgres:16-alpine`) |
| `kubernetes_service` | `k8s-platform` | Service `postgres:5432` (ClusterIP) |
| `helm_release` | `k8s-platform` | metrics-server em `kube-system` (HPA) |

```text
infra/environments/local
├── module.cluster   → kind cluster "oficina"
└── module.platform  → namespace + postgres + metrics-server
```

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) em execução
- [Terraform](https://developer.hashicorp.com/terraform/downloads) >= 1.5
- [kubectl](https://kubernetes.io/docs/tasks/tools/) (opcional, para inspeção)
- [kind](https://kind.sigs.k8s.io/) CLI (opcional — o provider cria o cluster)

## Estrutura

```
infra/
├── README.md
├── modules/
│   ├── kind-cluster/     # cluster kind
│   └── k8s-platform/     # namespace, Postgres, metrics-server
└── environments/
    └── local/            # ambiente local (kind)
```

## Como aplicar

```bash
cd infra/environments/local

# Opcional: copiar variáveis
cp terraform.tfvars.example terraform.tfvars

terraform init
terraform plan
terraform apply
```

### Outputs

Após o `apply`:

```bash
export KUBECONFIG="$(terraform output -raw kubeconfig_path)"
kubectl get nodes
kubectl get pods -n oficina
terraform output -raw database_url   # sensível — URL para DATABASE_URL da API
```

| Output | Uso |
|--------|-----|
| `kubeconfig_path` | `export KUBECONFIG=...` |
| `kubectl_context_hint` | Contexto `kind-oficina` |
| `namespace` | Namespace da aplicação |
| `database_url` | Conexão Postgres interno (`postgres:5432`) |

## Deploy da aplicação (após Terraform)

O Terraform provisiona **plataforma** (cluster + banco). A **API** continua sendo deployada pelos manifestos em `k8s/`:

```bash
# Na raiz do projeto (aula-1/)
export KUBECONFIG="$(terraform -chdir=infra/environments/local output -raw kubeconfig_path)"

docker build -t oficina-api:latest .
kind load docker-image oficina-api:latest --name oficina

export IMAGE=oficina-api:latest
export JWT_SECRET="$(openssl rand -hex 32)"
export WEBHOOK_API_KEY="dev-webhook-key"
export SKIP_PLATFORM=true
bash scripts/k8s-deploy.sh
```

`SKIP_PLATFORM=true` evita reaplicar `namespace.yaml` e `postgres.yaml` (já gerenciados pelo Terraform).

## Destruir infraestrutura

```bash
cd infra/environments/local
terraform destroy
```

Remove o cluster kind e recursos Kubernetes gerenciados pelo state.

## Relação com CI/CD e manifestos YAML

| Cenário | Cluster | Postgres | API |
|---------|---------|----------|-----|
| **Local + Terraform** | `terraform apply` | Terraform (`k8s-platform`) | `k8s-deploy.sh` com `SKIP_PLATFORM=true` |
| **CI/CD (GitHub Actions)** | Cluster remoto (`KUBECONFIG_DATA`) | `k8s/postgres.yaml` via `k8s-deploy.sh` | Mesmo script, sem `SKIP_PLATFORM` |
| **Manual sem Terraform** | kind/minikube existente | `kubectl apply -f k8s/postgres.yaml` | `k8s-deploy.sh` completo |

Os manifestos em [`k8s/`](../k8s/) permanecem a fonte de verdade para CI/CD; o Terraform espelha namespace e Postgres para provisionamento local declarativo.

## Variáveis principais

Ver [`environments/local/terraform.tfvars.example`](environments/local/terraform.tfvars.example):

- `cluster_name` — default `oficina`
- `node_image` — default `kindest/node:v1.29.2`
- `postgres_user` / `postgres_password` / `postgres_db` — default `oficina`
- `storage_size` — default `1Gi`

> **Nota acadêmica:** credenciais demo (`oficina`/`oficina`) são aceitáveis para entrega local. Em produção, use secrets externos e não versione senhas reais.
