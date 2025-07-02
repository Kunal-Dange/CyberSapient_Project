resource "aws_s3_bucket" "terraform" {
  bucket = "tf-bucket"

  tags = {
    Name        = "terraform"
    Environment = var.target_infra
  }
}