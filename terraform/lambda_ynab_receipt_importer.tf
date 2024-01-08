# data "archive_file" "ynab_ri_function_lambda_zip" {
#   type        = "zip"
#   source_dir  = "${path.module}/lambda/ynab_receipt_importer"
#   output_path = "/tmp/ynab_receipt_importer.zip"
# }

resource "aws_iam_role" "ynab_receipt_importer_role" {
  assume_role_policy = jsonencode({
    "Statement" : [
      {
        "Action" : "sts:AssumeRole",
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "lambda.amazonaws.com"
        }
      }
    ],
    "Version" : "2012-10-17"
  })
  description           = "Role to grant access to YNAB receipt importer permissions"
  force_detach_policies = false
  managed_policy_arns   = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole", "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"]
  max_session_duration  = 3600
  name                  = "ynab-receipt-importer-role"
  path                  = "/"
  // TODO: tighten this policy, add specific resources
  inline_policy {
    name = "ynab-receipt-importer-policy"
    policy = jsonencode({
      "Statement" : [
        {
          "Action" : [
            "secretsmanager:GetSecretValue",
          ],
          "Effect" : "Allow",
          "Resource" : "arn:aws:secretsmanager:${local.region}:${data.aws_caller_identity.current.account_id}:secret:openapi-key"
        }
      ]
      "Version" : "2012-10-17"
    })
  }

  tags = {
    Name = "ynab-receipt-importer-role"
  }
}

resource "aws_lambda_function" "ynab_receipt_importer_function" {
  architectures = ["x86_64"]
  description   = "Function to import receipts into YNAB"
  function_name = "ynab-receipt-importer"
  # handler                        = "main.lambda_handler"
  memory_size                    = 128
  package_type                   = "Image"
  image_uri                      = "cmaahs/ynabri:0.0.1"
  reserved_concurrent_executions = -1
  role                           = aws_iam_role.ynab_receipt_importer_role.arn
  # runtime                        = "python3.11"
  skip_destroy = false
  #  source_code_hash               = data.archive_file.ynab_ri_function_lambda_zip.output_base64sha256
  timeout = 60
  ephemeral_storage {
    size = 512
  }
  tracing_config {
    mode = "PassThrough"
  }

  tags = {
    Name = "ynab-receipt-importer"
  }

  depends_on = [
    aws_iam_role.ynab_receipt_importer_role,
    aws_ecr_repository.ynabri_repositories,
  ]
}
