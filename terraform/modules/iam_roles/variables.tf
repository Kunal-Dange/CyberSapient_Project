variable "roles_json" {
    description = "JSON string containing IAM roles and policies"
    type        = any
    # default = []
  
}

variable "tags" {
    description = "Tags to apply to the IAM roles"
    type        = map
    # default     = []
  
}