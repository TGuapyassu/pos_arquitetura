output "namespace" {
  description = "Namespace da aplicação."
  value       = kubernetes_namespace.oficina.metadata[0].name
}

output "database_url" {
  description = "URL de conexão JDBC/SQLAlchemy para a API (Postgres interno)."
  value       = "postgresql+psycopg2://${var.postgres_user}:${var.postgres_password}@postgres:5432/${var.postgres_db}"
  sensitive   = true
}

output "database_host" {
  description = "Hostname interno do Service PostgreSQL."
  value       = kubernetes_service.postgres.metadata[0].name
}

output "database_port" {
  description = "Porta do Service PostgreSQL."
  value       = kubernetes_service.postgres.spec[0].port[0].port
}
