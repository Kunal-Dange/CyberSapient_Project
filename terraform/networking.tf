module "vpc" {
    source = "./modules/vpc"
    cidr_block = "100.10.0.0/24"
    vpc_name = "CyberSapient-VPC"
    app_env = "dev1"
}

output "vpc_id" {
  value = module.vpc.vpc_id
}
data "aws_availability_zones" "available" {}

resource "aws_subnet" "public" {
  count                   = length(data.aws_availability_zones.available.names)
  vpc_id                  = module.vpc.vpc_id
  cidr_block              = cidrsubnet(module.vpc.cidr_block, 4, count.index)
  map_public_ip_on_launch = true
  availability_zone       = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "CyberSapient-public-${count.index}"
  }
}

resource "aws_subnet" "private" {
  count             = length(data.aws_availability_zones.available.names)
  vpc_id            = module.vpc.vpc_id
  cidr_block        = cidrsubnet(module.vpc.cidr_block, 4, count.index + 10)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "CyberSapient-private-${count.index}"
  }
}





