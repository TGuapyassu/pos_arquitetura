#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
K8S_DIR="${ROOT_DIR}/k8s"
NAMESPACE="${NAMESPACE:-oficina}"

: "${IMAGE:?IMAGE is required}"

JWT_SECRET="${JWT_SECRET:-}"
WEBHOOK_API_KEY="${WEBHOOK_API_KEY:-}"
DATABASE_URL="${DATABASE_URL:-postgresql+psycopg2://oficina:oficina@postgres:5432/oficina}"
SMTP_USER="${SMTP_USER:-}"
SMTP_PASSWORD="${SMTP_PASSWORD:-}"

if [[ -z "${JWT_SECRET}" || -z "${WEBHOOK_API_KEY}" ]]; then
  echo "JWT_SECRET and WEBHOOK_API_KEY must be set." >&2
  exit 1
fi

SKIP_PLATFORM="${SKIP_PLATFORM:-false}"

if [[ "${SKIP_PLATFORM}" == "true" ]]; then
  echo "==> Plataforma (namespace + Postgres) gerenciada externamente — pulando"
else
  echo "==> Namespace"
  kubectl apply -f "${K8S_DIR}/namespace.yaml"

  echo "==> PostgreSQL (Secret, PVC, StatefulSet, Service)"
  kubectl apply -f "${K8S_DIR}/postgres.yaml"
fi

echo "==> Aguardando Postgres ficar pronto"
kubectl wait --for=condition=ready pod -l app=postgres -n "${NAMESPACE}" --timeout=180s

echo "==> ConfigMap da API"
kubectl apply -f "${K8S_DIR}/configmap.yaml"

echo "==> Secret da API"
kubectl create secret generic oficina-secrets -n "${NAMESPACE}" \
  --from-literal=DATABASE_URL="${DATABASE_URL}" \
  --from-literal=JWT_SECRET="${JWT_SECRET}" \
  --from-literal=WEBHOOK_API_KEY="${WEBHOOK_API_KEY}" \
  --from-literal=SMTP_USER="${SMTP_USER}" \
  --from-literal=SMTP_PASSWORD="${SMTP_PASSWORD}" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "==> Migration Job (imagem: ${IMAGE})"
kubectl delete job oficina-api-migration -n "${NAMESPACE}" --ignore-not-found
sed "s|oficina-api:latest|${IMAGE}|g" "${K8S_DIR}/migration-job.yaml" | kubectl apply -f -

echo "==> Aguardando migrations"
kubectl wait --for=condition=complete job/oficina-api-migration -n "${NAMESPACE}" --timeout=180s

echo "==> Deployment, Service e HPA (imagem: ${IMAGE})"
sed "s|oficina-api:latest|${IMAGE}|g" "${K8S_DIR}/deployment.yaml" | kubectl apply -f -
kubectl apply -f "${K8S_DIR}/service.yaml" -f "${K8S_DIR}/hpa.yaml"

echo "==> Aguardando rollout da API"
kubectl rollout status deployment/oficina-api -n "${NAMESPACE}" --timeout=180s

echo "Deploy concluído."
kubectl get pods,svc,hpa -n "${NAMESPACE}"
