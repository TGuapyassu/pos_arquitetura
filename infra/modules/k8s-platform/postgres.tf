resource "kubernetes_secret" "postgres" {
  metadata {
    name      = "postgres-secrets"
    namespace = kubernetes_namespace.oficina.metadata[0].name
    labels = {
      "app.kubernetes.io/name"    = "postgres"
      "app.kubernetes.io/part-of" = "oficina"
    }
  }

  type = "Opaque"

  string_data = {
    POSTGRES_USER     = var.postgres_user
    POSTGRES_PASSWORD = var.postgres_password
    POSTGRES_DB       = var.postgres_db
  }

  depends_on = [kubernetes_namespace.oficina]
}

resource "kubernetes_persistent_volume_claim" "postgres" {
  metadata {
    name      = "postgres-data"
    namespace = kubernetes_namespace.oficina.metadata[0].name
    labels = {
      "app.kubernetes.io/name" = "postgres"
    }
  }

  spec {
    access_modes = ["ReadWriteOnce"]
    resources {
      requests = {
        storage = var.storage_size
      }
    }
  }

  depends_on = [kubernetes_namespace.oficina]
}

resource "kubernetes_stateful_set" "postgres" {
  metadata {
    name      = "postgres"
    namespace = kubernetes_namespace.oficina.metadata[0].name
    labels = {
      "app.kubernetes.io/name" = "postgres"
    }
  }

  spec {
    service_name = "postgres"
    replicas     = 1

    selector {
      match_labels = {
        app = "postgres"
      }
    }

    template {
      metadata {
        labels = {
          app                         = "postgres"
          "app.kubernetes.io/name"    = "postgres"
        }
      }

      spec {
        container {
          name  = "postgres"
          image = var.postgres_image

          port {
            name           = "postgres"
            container_port = 5432
            protocol       = "TCP"
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.postgres.metadata[0].name
            }
          }

          volume_mount {
            name       = "postgres-data"
            mount_path = "/var/lib/postgresql/data"
          }

          liveness_probe {
            exec {
              command = ["pg_isready", "-U", var.postgres_user, "-d", var.postgres_db]
            }
            initial_delay_seconds = 15
            period_seconds        = 10
            timeout_seconds       = 5
            failure_threshold     = 3
          }

          readiness_probe {
            exec {
              command = ["pg_isready", "-U", var.postgres_user, "-d", var.postgres_db]
            }
            initial_delay_seconds = 5
            period_seconds        = 5
            timeout_seconds       = 3
            failure_threshold     = 3
          }

          resources {
            requests = {
              cpu    = "100m"
              memory = "256Mi"
            }
            limits = {
              cpu    = "500m"
              memory = "512Mi"
            }
          }
        }

        volume {
          name = "postgres-data"
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim.postgres.metadata[0].name
          }
        }
      }
    }
  }

  depends_on = [
    kubernetes_secret.postgres,
    kubernetes_persistent_volume_claim.postgres,
  ]
}

resource "kubernetes_service" "postgres" {
  metadata {
    name      = "postgres"
    namespace = kubernetes_namespace.oficina.metadata[0].name
    labels = {
      "app.kubernetes.io/name" = "postgres"
    }
  }

  spec {
    type = "ClusterIP"

    selector = {
      app = "postgres"
    }

    port {
      name        = "postgres"
      port        = 5432
      target_port = "postgres"
      protocol    = "TCP"
    }
  }

  depends_on = [kubernetes_stateful_set.postgres]
}
