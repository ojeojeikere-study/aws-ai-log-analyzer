terraform {
  backend "s3" {
    bucket         = "your-terraform-state-bucket"
    key            = "aws-ai-log-analyzer/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.region
}

resource "aws_s3_bucket" "results" {
  bucket = "ai-log-analysis-results"
}

resource "aws_sns_topic" "alerts" {
  name = "ai-log-analyzer-alerts"
}

resource "aws_iam_role" "lambda_role" {
  name = "ai-log-analyzer-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Principal = { Service = "lambda.amazonaws.com" },
      Effect = "Allow"
    }]
  })
}

resource "aws_lambda_function" "log_analyzer" {
  function_name = "ai-log-analyzer"
  runtime       = "python3.9"
  handler       = "log_analyzer.lambda_handler"
  role          = aws_iam_role.lambda_role.arn
  filename      = "../lambda/log_analyzer.zip"

  environment {
    variables = {
      LOG_GROUP_NAME = "/aws/lambda/example"
      S3_BUCKET_NAME = aws_s3_bucket.results.bucket
      LLM_API_URL    = "https://api.llm-endpoint.com/v1/analyze"
      LLM_API_KEY    = "YOUR_API_KEY"
      SNS_TOPIC_ARN  = aws_sns_topic.alerts.arn
    }
  }
}

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/ai-log-analyzer"
  retention_in_days = 14
}
