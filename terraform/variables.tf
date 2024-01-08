variable "common_tags" {
  type        = map(string)
  description = "A MAP of key/value values to apply as AWS Tags to ALL Resources"
  # individual resource will add: name, tf-module, type
  default = {
    product   = "ynab-receipt-importer"
    acct_code = "dmaahs2017"
  }
}

variable "openapi_key" {
  type        = string
  description = "set TF_VAR_openapi_key environment varaible"
}