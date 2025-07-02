variable "iam_roles" {
  description = "Map of IAM roles to create"
  type = map(object({
    name                = string
    assume_role_policy  = string
    description         = string
    max_session_duration = number
    tags                = map(string)
  }))
}

variable "iam_role_policies" {
  description = "Map of IAM role policies to attach"
  type = map(object({
    name      = string
    role_name = string
    policy    = string
  }))
}

variable "managed_policies" {
  description = "Map of managed policies to attach to roles"
  type = map(object({
    name      = string
    role_name = string
    policy_arn = string
  }))
}