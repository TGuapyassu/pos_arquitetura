variable "cluster_name" {
  description = "Nome do cluster kind."
  type        = string
  default     = "oficina"
}

variable "node_image" {
  description = "Imagem kindest/node."
  type        = string
  default     = "kindest/node:v1.29.2"
}

variable "kubeconfig_path" {
  description = "Caminho do kubeconfig (vazio = padrão ~/.kube/kind-<nome>)."
  type        = string
  default     = ""
}

variable "worker_nodes" {
  description = "Nós worker do cluster."
  type        = number
  default     = 1
}

variable "namespace" {
  description = "Namespace Kubernetes da aplicação."
  type        = string
  default     = "oficina"
}

variable "postgres_user" {
  description = "Usuário PostgreSQL."
  type        = string
  default     = "oficina"
}

variable "postgres_password" {
  description = "Senha PostgreSQL."
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
  description = "Tamanho do PVC do PostgreSQL."
  type        = string
  default     = "1Gi"
}

variable "install_metrics_server" {
  description = "Instalar metrics-server para HPA."
  type        = bool
  default     = true
}
