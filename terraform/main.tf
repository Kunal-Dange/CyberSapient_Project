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
}

data "aws_eks_cluster" "cluster" {
  name = "${var.environment}-cluster"
}

data "aws_eks_cluster_auth" "cluster" {
  name = "${var.environment}-cluster"
  }
  
  provider "helm" {
    kubernetes {
      config_path = "~/.kube/config"
  }
}

resource "helm_release" "frontend" {
  name       = "frontend"
  namespace  = var.environment
  create_namespace = true
  chart      = "${path.module}/helm"

  values = [file("${path.module}/helm/values-${var.environment}.yaml")]
}