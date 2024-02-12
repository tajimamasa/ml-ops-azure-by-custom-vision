# ML OPS with Custom Vision

## デプロイ

### Terraform

`./terraform/terraform.tfvars.sample`を`.sample`を外してコピーし、必要事項を記入します。
以下のコマンドで terraform で Azure 環境を構築します。

```
cd terraform
terraform init
terraform plan
terraform apply
```

## ローカル実行

`./src/local.settings.json.sample`を`.sample`を外してコピーし、StorageConnection を記入します。
以下のコマンドでローカル実行します。

```
cd src
func start
```
