module "cluster" {
  source = "../../modules/kind-cluster"

  cluster_name    = var.cluster_name
  node_image      = var.node_image
  kubeconfig_path = var.kubeconfig_path
  worker_nodes    = var.worker_nodes
}

module "platform" {
  source = "../../modules/k8s-platform"

  namespace              = var.namespace
  postgres_user          = var.postgres_user
  postgres_password      = var.postgres_password
  postgres_db            = var.postgres_db
  postgres_image         = var.postgres_image
  storage_size           = var.storage_size
  install_metrics_server = var.install_metrics_server

  depends_on = [module.cluster]
}
