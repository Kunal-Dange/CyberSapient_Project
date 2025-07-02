module "vpc" {
    source = "./modules/vpc"
    cidr_block = "100.10.0.0/24"
    vpc_name = "CyberSapient-VPC"
    app_env = "dev"
}