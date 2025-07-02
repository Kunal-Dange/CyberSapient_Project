output "iam_roles" {
  description = "IAM roles created"
  value = aws_iam_role.roles
}

output "iam_role_policies" {
  description = "IAM role policies created"
  value = aws_iam_role_policy.policy
}

output "policy_attachments" {
  description = "IAM policy attachments created"
  value = aws_iam_policy_attachment.policy_attachment
}