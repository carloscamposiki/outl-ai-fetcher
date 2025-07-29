resource "aws_lambda_function" "lambda_function" {
  function_name = var.lambda_name
  role          = var.role_arn
  runtime       = "python3.11"
  handler       = "main.lambda_handler"

  filename         = "${path.module}/lambda.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda.zip")

  environment {
    variables = {
      TOKEN_SECRET_NAME = "ool/bluesky/token",
      BLUE_SKY_CREDENTIALS_SECRET_NAME = "ool/bluesky/credentials",
      TRENDS_PROCESSING_QUEUE = var.queue_processing_trends,
      DYNAMO_TRENDS_TABLE_NAME = var.dynamo_trends_table_name
    }
  }

  timeout = 10
  memory_size = 128
}
