resource "kubernetes_namespace" "oficina" {
  metadata {
    name = var.namespace
    labels = {
      "app.kubernetes.io/name"    = "oficina-api"
      "app.kubernetes.io/part-of" = "oficina"
    }
  }
}
