variable "environment" {
  description = "Deployment environment (e.g. prod, nonprod)"
  type        = string
}
variable "cluster_name" {
  type        = string
  description = "Name of the EKS cluster"
  default = "cybersapient-eks"
}

variable "vpc_name" {
  default = "cybersapient"
}

variable "grafana_admin_password" {
  description = "Admin password for Grafana"
  type        = string
  default     = "CyberSapient"
  sensitive   = true
}


