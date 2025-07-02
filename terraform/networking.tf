module "vpc" {
    source = "./modules/vpc"
    cidr_block = "100.10.0.0/24"
    vpc_name = "${var.environment}-${var.app_env}-vpc"
    app_env = "dev1"
}