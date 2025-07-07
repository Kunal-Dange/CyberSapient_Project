# AWS Secrets Manager for application secrets
resource "aws_secretsmanager_secret" "app_secrets" {
  name        = "${var.environment}-app-secrets"
  description = "Application secrets for ${var.environment} environment"

  tags = {
    Environment = var.environment
    Project     = "CyberSapient"
  }
}

resource "aws_secretsmanager_secret_version" "app_secrets_version" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    database_url = "postgresql://user:password@${var.environment}-db.cybersapient.local:5432/app"
    api_key      = "sk-${var.environment}-${random_string.api_key.result}"
    jwt_secret   = random_string.jwt_secret.result
    grafana_password = var.grafana_admin_password
  })
}

# Random strings for secrets
resource "random_string" "api_key" {
  length  = 32
  special = false
}

resource "random_string" "jwt_secret" {
  length  = 64
  special = false
}

# IAM policy for EKS to access secrets
resource "aws_iam_policy" "secrets_access" {
  name        = "${var.environment}-secrets-access"
  description = "Policy for accessing secrets in ${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = aws_secretsmanager_secret.app_secrets.arn
      }
    ]
  })
}

# Attach secrets policy to EKS node role
resource "aws_iam_role_policy_attachment" "eks_secrets_access" {
  role       = aws_iam_role.eks_node_group_role.name
  policy_arn = aws_iam_policy.secrets_access.arn
} 