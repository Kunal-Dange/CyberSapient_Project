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