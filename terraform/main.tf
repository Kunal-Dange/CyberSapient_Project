terraform {
  backend "s3" {
    bucket         = "kd-kubernetes"
    key            = "terraform.tfstate"
    region         = "ap-south-1"
  }
}

provider "aws" {
    region = "ap-south-1" 
}

provider "tls" {}
  
