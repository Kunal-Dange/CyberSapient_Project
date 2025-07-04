resource "aws_eks_cluster" "this" {
  name     = "${var.environment}-cluster-role"
  role_arn = aws_iam_role.eks_cluster_role

  vpc_config {
    subnet_ids = [aws_subnet.public.*.id, aws_subnet.private.*.id]
  }

  kubernetes_network_config {
    service_ipv4_cidr = "172.20.0.0/16"
  }

  depends_on = [aws_iam_role.eks_cluster_role]
}

resource "aws_eks_node_group" "this" {
  cluster_name    = aws_eks_cluster.this.name
  node_group_name = "${var.cluster_name}-node-group"
  node_role_arn   = aws_iam_role.eks_node_role.arn
  subnet_ids      = [aws_subnet.public.*.id, aws_subnet.private.*.id]

  scaling_config {
    desired_size = 2
    max_size     = 3
    min_size     = 1
  }

  instance_types = ["t3.medium"]

  depends_on = [aws_iam_role.eks_node_role.arn]
}

output "cluster_name" {
  value = aws_eks_cluster.this.name
}

output "cluster_endpoint" {
  value = aws_eks_cluster.this.endpoint
}

output "oidc_provider_arn" {
  value = aws_eks_cluster.this.identity[0].oidc[0].issuer
}
