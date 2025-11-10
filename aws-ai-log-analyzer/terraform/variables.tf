variable "region" { description = "AWS region" default = "us-east-1" }
variable "terraform_state_bucket" { description = "S3 bucket for Terraform remote state" default = "your-terraform-state-bucket" }
variable "dynamodb_lock_table" { description = "DynamoDB table for state locking" default = "terraform-locks" }
