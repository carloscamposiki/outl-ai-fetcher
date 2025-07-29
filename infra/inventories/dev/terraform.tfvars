lambda_name         = "lambda-ool-fetcher-dev"
role_arn            = "arn:aws:iam::496993584089:role/ool-fetcher-role"
vpc_id              = "vpc-0dd33b8fbb5ce6aac"
subnet_ids          = ["subnet-05087d6661c904373", "subnet-03865d617507188de"]
security_group_ids  = ["sg-09fc456c54e2a9669"]
dynamo_trends_table_name = "ool-bluesky-trends-dev"
queue_processing_trends  = "ool-bluesky-trends-processing-queue-dev"