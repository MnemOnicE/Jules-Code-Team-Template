# AWS OIDC Provider Configuration
# This Terraform configuration establishes the trust relationship between GitHub Actions and AWS.

variable "github_org" {
  description = "The GitHub Organization name"
  type        = string
}

variable "github_repo" {
  description = "The GitHub Repository name"
  type        = string
}

variable "github_branch" {
  description = "The GitHub branch allowed to assume this role"
  type        = string
  default     = "main"
}

data "tls_certificate" "github" {
  url = "https://token.actions.githubusercontent.com/.well-known/openid-configuration"
}

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.github.certificates[0].sha1_fingerprint]
}

resource "aws_iam_role" "github_actions" {
  name = "github-actions-oidc-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_org}/${var.github_repo}:ref:refs/heads/${var.github_branch}"
          }
        }
      }
    ]
  })
}

output "role_arn" {
  value = aws_iam_role.github_actions.arn
}
