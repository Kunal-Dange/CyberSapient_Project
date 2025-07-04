terraform {
  backend "s3" {
    bucket         = "kd-kubernetes"
    key            = "terraform/terraform.tfstate"
    region         = "us-east-1"
  }
}

provider "aws" {
    region = "us-east-1" 
}

provider "tls" {}
  
provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.cluster.token
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = [
      "eks",
      "get-token",
      "--cluster-name",
      data.aws_eks_cluster.cluster.name,
    ]
  }
}

data "aws_eks_cluster" "cluster" {
  name = "${var.environment}-cluster"
}

data "aws_eks_cluster_auth" "cluster" {
  name = "${var.environment}-cluster"
  }
  
