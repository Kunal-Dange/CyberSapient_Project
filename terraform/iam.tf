module "iam_roles" {
  source = "./modules/iam_roles"
  iam_roles = {
    role1 = {
      name                = "example-role"
      assume_role_policy  = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
      description         = "Example IAM Role"
      max_session_duration = 3600
      tags = {
        Environment = "Dev"
      }
    }
  }

  iam_role_policies = {
    policy1 = {
      name      = "example-policy"
      role_name = "role1" # Use the key from iam_roles, not the role name
      policy    = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": "*"
    }
  ]
}
EOF
    }
  }

  managed_policies = {
    attachment1 = {
      name      = "example-attachment"
      role_name = "role1" # Use the key from iam_roles, not the role name
      policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
    }
  }
}