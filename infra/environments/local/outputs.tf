output "cluster_name" {
  description = "Nome do cluster kind."
  value       = module.cluster.cluster_name
}

output "kubeconfig_path" {
  description = "Caminho do kubeconfig — use: export KUBECONFIG=$(terraform output -raw kubeconfig_path)"
  value       = module.cluster.kubeconfig_path
}

output "kubectl_context_hint" {
  description = "Contexto kubectl sugerido."
  value       = "kind-${module.cluster.cluster_name}"
}

output "namespace" {
  description = "Namespace da aplicação."
  value       = module.platform.namespace
}

output "database_url" {
  description = "DATABASE_URL para a API (Postgres interno no cluster)."
  value       = module.platform.database_url
  sensitive   = true
}

output "database_host" {
  description = "Hostname do Service PostgreSQL."
  value       = module.platform.database_host
}
