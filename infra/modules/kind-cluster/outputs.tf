output "cluster_name" {
  description = "Nome do cluster kind."
  value       = kind_cluster.this.name
}

output "kubeconfig_path" {
  description = "Caminho absoluto do kubeconfig do cluster."
  value       = kind_cluster.this.kubeconfig_path
}

output "endpoint" {
  description = "Endpoint da API do cluster."
  value       = kind_cluster.this.endpoint
}
