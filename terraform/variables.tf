variable "environment" {
  description = "Deployment environment (e.g. prod, nonprod)"
  type        = string
}
variable "cluster_name" {
  type        = string
  description = "Name of the EKS cluster"
  default = "cybersapient-eks"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID"
}

variable "vpc_name" {
  default = "cybersapient"
}

variable "public_subnets" {
  type        = list(string)
  description = "List of public subnet IDs"
}

variable "private_subnets" {
  type        = list(string)
  description = "List of private subnet IDs"
}

