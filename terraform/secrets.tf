// OPENAI_API_KEY
resource "aws_secretsmanager_secret" "openapi_key" {
  description             = "openapi api key"
  name                    = "openapi-key"
  recovery_window_in_days = 0

  tags = merge(local.common_tags, {
    Name = "openapi-key"
  })
}

resource "aws_secretsmanager_secret_version" "platform_prod_secret_values" {
  secret_id     = aws_secretsmanager_secret.openapi_key.id
  secret_string = var.openapi_key
}