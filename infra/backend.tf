terraform {
  backend "s3" {
    bucket         = "4969-9358-4089-terraform-state"
    key            = terraform.workspace
    region         = "us-east-1"
  }
}
