variable "cluster_name" {
  description = "Nome do cluster kind."
  type        = string
  default     = "oficina"
}

variable "node_image" {
  description = "Imagem dos nós kind (kindest/node)."
  type        = string
  default     = "kindest/node:v1.29.2"
}

variable "kubeconfig_path" {
  description = "Caminho do kubeconfig gerado pelo kind."
  type        = string
  default     = ""
}

variable "worker_nodes" {
  description = "Quantidade de nós worker."
  type        = number
  default     = 1
}
