resource "kubernetes_namespace" "cybersapient_namespace" {
  metadata {
    annotations = {
      name = "${var.environment}"
    }

    labels = {
      mylabel = "CST-NS"
    }

    name = "${var.environment}"
  }
}