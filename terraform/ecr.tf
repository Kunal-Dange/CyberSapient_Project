resource "aws_ecr_repository" "example" {
  name                 = "cybersapient-ecr-repo"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "CyberSapient ECR Repository"
    Environment = "${var.environment}"
  }
}

output "ecr_repository_url" {
  value = aws_ecr_repository.example.repository_url
  description = "URL of the ECR repository"
}