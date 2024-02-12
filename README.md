# ML OPS with Custom Vision

## デプロイ

### Terraform

以下のコマンドで terraform で Azure 環境を構築します。

```
cd terraform
terraform init
terraform plan
terraform apply
```

## ローカル実行

`./src/local.settings.json.sample`を`.sample`を外してコピーし、StorageConnection を埋めてください。
以下のコマンドでローカル実行します。

```
cd src
func start
```
