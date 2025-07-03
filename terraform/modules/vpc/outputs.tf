
output "cidr_block" {
  value       = aws_vpc.main.cidr_block
  description = "The CIDR block of the VPC"
}

output "vpc_id" {
  value = module.main.vpc_id
}