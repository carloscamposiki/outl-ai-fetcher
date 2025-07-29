resource "aws_lambda_function" "this" {
  function_name = var.lambda_name
  role          = var.role_arn
  runtime       = "python3.11"
  handler       = "main.lambda_handler"

  filename         = "${path.module}/lambda.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda.zip")

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }

  environment {
    variables = {
      ENV = "example"
    }
  }

  timeout = 10
  memory_size = 128
}
