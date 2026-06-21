provider "kind" {}

provider "kubernetes" {
  config_path = module.cluster.kubeconfig_path
}

provider "helm" {
  kubernetes {
    config_path = module.cluster.kubeconfig_path
  }
}
