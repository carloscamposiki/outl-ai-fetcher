variable "lambda_name" {
  description = "The name of the Lambda function"
  type        = string
}

variable "role_arn" {
  description = "The IAM role ARN for the Lambda function"
  type        = string
}

variable "vpc_id" {
  description = "The VPC where the Lambda will be deployed"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs to attach the Lambda to"
  type        = list(string)
}

variable "security_group_ids" {
  description = "List of security groups for Lambda networking"
  type        = list(string)
}

variable "dynamo_trends_table_name" {
  description = "The name of the DynamoDB table for trends"
  type        = string
}

variable "queue_processing_trends" {
    description = "The SQS queue for processing trends"
    type        = string
}
