resource "kind_cluster" "this" {
  name            = var.cluster_name
  node_image      = var.node_image
  kubeconfig_path = var.kubeconfig_path != "" ? pathexpand(var.kubeconfig_path) : pathexpand("~/.kube/kind-${var.cluster_name}")
  wait_for_ready  = true

  kind_config {
    kind        = "Cluster"
    api_version = "kind.x-k8s.io/v1alpha4"

    node {
      role = "control-plane"
    }

    dynamic "node" {
      for_each = range(var.worker_nodes)
      content {
        role = "worker"
      }
    }
  }
}
