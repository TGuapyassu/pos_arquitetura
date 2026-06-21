variable "namespace" {
  description = "Namespace da aplicação."
  type        = string
  default     = "oficina"
}

variable "postgres_user" {
  description = "Usuário do PostgreSQL."
  type        = string
  default     = "oficina"
}

variable "postgres_password" {
  description = "Senha do PostgreSQL."
  type        = string
  default     = "oficina"
  sensitive   = true
}

variable "postgres_db" {
  description = "Nome do banco PostgreSQL."
  type        = string
  default     = "oficina"
}

variable "postgres_image" {
  description = "Imagem Docker do PostgreSQL."
  type        = string
  default     = "postgres:16-alpine"
}

variable "storage_size" {
  description = "Tamanho do PVC de dados do PostgreSQL."
  type        = string
  default     = "1Gi"
}

variable "install_metrics_server" {
  description = "Instalar metrics-server (necessário para HPA)."
  type        = bool
  default     = true
}
