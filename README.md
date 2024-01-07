# ML OPS with Custom Vision

こちらは Azure の Custom Vision を用いた、
ML Ops のサービスです。

実際のカメラ環境に適した推論モデルを構築します。
推論モデルで物体認識した人間のカウントを行います。

## システム構成

### インフラ

TBD

### API エンドポイント

#### Learning

以下のシナリオで再学習を行うため API です。

1. 画像をアップロード
1. 指定した画像で再学習

ローカル実行時に[Open API](0.0.0.0:8000/docs/)から確認できます。

#### Counting

TBD

## デプロイ

TBD

## ローカル実行

```
docker compose -f docker-compose-localdev.yml up --build -d
```

## ToDo

- 再学習用 API の実装
- Terraform の整備
- GitHub Actions の構築
- 学習済み API の実装
