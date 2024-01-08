locals {
  common_tags = merge(var.common_tags, {
    tf-module = "root"
  })

  region = "us-east-1"

  repository_list = [
    "ynabri",
  ]
}