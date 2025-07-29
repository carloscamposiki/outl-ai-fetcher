variable "lambda_name" {
  description = "The name of the Lambda function"
  type        = string
}

variable "role_arn" {
  description = "The IAM role ARN for the Lambda function"
  type        = string
}

variable "dynamo_trends_table_name" {
  description = "The name of the DynamoDB table for trends"
  type        = string
}

variable "queue_processing_trends" {
    description = "The SQS queue for processing trends"
    type        = string
}
