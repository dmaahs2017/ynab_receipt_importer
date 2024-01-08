resource "aws_lambda_function_url" "restricted_url" {
  function_name      = aws_lambda_function.ynab_receipt_importer_function.function_name
  authorization_type = "AWS_IAM"

  # TODO: review these
  cors {
    allow_credentials = true
    allow_origins     = ["*"]
    allow_methods     = ["*"]
    allow_headers     = ["date", "keep-alive"]
    expose_headers    = ["keep-alive", "date"]
  }
}
