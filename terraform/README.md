# Testing

## Creating the Infrastructure by Running Terraform

### Set Credentials

```shell
# supply your values for these items
export TF_VAR_openapi_key=
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
```

### Run the plan

This will output the "changes" terraform is looking to make, review them prior to the apply stage

```shell
# install terraform 'brew install terraform --formula'
cd terraform
terraform plan -out plan.out
```

### Apply the plan

```shell
terraform apply plan.out
```

## Destroying the Infrastructure by Using Terraform

### Run the destroy plan

Like the "plan" plan, this will spit out a list of things to destroy, review then proceed

```shell
terraform plan -destroy -out plan.out
```

### Run the destroy apply

```shell
# this mechanism is always scary, since the command is the same for create and destroy
terraform apply plan.out
```

## Test from LAMBDA

The value of `Receipt` in the JSON would be the data from:

```shell
cat imgs/auto_store.jpg | base64 -w0 | pbcopy
```

```json
{
  "RequestType": "put",
  "YnabKey": "empty",
  "BudgetId": "00d897bf-4703-4976-af2a-35d1bdc9b673",
  "DryRun": "true",
  "Receipt": ""
}
```
