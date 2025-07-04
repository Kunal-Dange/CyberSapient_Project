resource "aws_eks_cluster" "this" {
  name     = "${var.environment}-cluster"
  role_arn = aws_iam_role.eks_cluster_role.arn

  vpc_config {
    subnet_ids = concat(aws_subnet.public[*].id, aws_subnet.private[*].id)
  }

  kubernetes_network_config {
    service_ipv4_cidr = "172.20.0.0/16"
  }

 
  depends_on = [aws_iam_role.eks_cluster_role]
}
resource "aws_eks_fargate_profile" "frontend_fargate" {
  cluster_name           = aws_eks_cluster.this.name
  fargate_profile_name   = "${var.environment}-fargate-profile"
  pod_execution_role_arn = aws_iam_role.fargate_pod_execution.arn
  subnet_ids             = aws_subnet.private[*].id

  selector {
    namespace = var.environment
  }

  depends_on = [aws_eks_cluster.this]
}
