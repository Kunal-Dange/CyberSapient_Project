terraform {
  backend "s3" {}
}

provider "aws" {
    region = "ap-south-1" 
}

provider "tls" {}
  
