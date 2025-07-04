
resource "kubernetes_namespace" "cybersapient_namespace" {
  metadata {
    name = var.environment
  }

  depends_on = [aws_eks_cluster.this]
}
