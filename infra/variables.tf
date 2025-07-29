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