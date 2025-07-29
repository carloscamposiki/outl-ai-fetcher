terraform {
  backend "s3" {
    bucket         = "4969-9358-4089-terraform-state"
    key            = "${terraform.workspace}/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
  }
}