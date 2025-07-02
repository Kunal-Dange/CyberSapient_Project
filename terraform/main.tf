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
  
