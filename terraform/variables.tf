variable "target_infra" {
    description = "Nonprod or Prod"
    default     = "Nonprod"
}

variable "environment" {
  description = "Environment name (prod/nonprod)"
  type        = string
}
variable "app_env" {
    description = "Application environment" 
}
