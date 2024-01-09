# docker -> lambda update

## update docker

```shell
cd docker
docker build -t 232611481816.dkr.ecr.us-east-1.amazonaws.com/ynabri:0.0.11 .
docker push 232611481816.dkr.ecr.us-east-1.amazonaws.com/ynabri:0.0.11
```

## update terraform

```shell
cd terraform
vi lambda_ynab_receipt_importer.tf
# edit the image line, update to the docker tag
terraform plan -out plan.out
terraform apply plan.out
```

## test lambda

```shell
# from repo root
./invoke-function.sh imgs/auto_store.jpg
```
