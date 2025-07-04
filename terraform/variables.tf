variable "target_infra" {
    description = "Nonprod or Prod"
    default     = "Nonprod"
}

variable "cluster_name" {
  type        = string
  description = "Name of the EKS cluster"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID"
}

variable "public_subnets" {
  type        = list(string)
  description = "List of public subnet IDs"
}

variable "private_subnets" {
  type        = list(string)
  description = "List of private subnet IDs"
}

variable "cluster_role_arn" {
  type        = string
  description = "IAM Role ARN for the EKS cluster"
}

variable "node_role_arn" {
  type        = string
  description = "IAM Role ARN for worker nodes"
}
