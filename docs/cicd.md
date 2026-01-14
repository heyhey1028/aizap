# CI/CD

GitHub Actions を使用して CI/CD を実現しています。

## ワークフロー

| ワークフロー | トリガー | 動作 |
|-------------|---------|------|
| `infra-plan.yml` | PR（infra/** 変更時） | `terraform plan` を実行 |
| `infra-release.yml` | main push / `infra-v*` タグ | `terraform apply` を実行 |
| `app-deploy.yml` | main push / `app-v*` タグ | BFF/Worker をビルド・デプロイ |
| `agent-deploy.yml` | workflow_dispatch | Agent Engine へエージェントをデプロイ |

## Composite Actions

再利用可能なロジックを Composite Action として切り出しています。

```
.github/actions/
├── cloud-build/           # Cloud Build でビルド・待機
├── decide-environment/    # 環境決定（dev/prod）
├── decide-services/       # デプロイ対象サービス決定
└── get-cloud-run-image/   # Cloud Run の現在のイメージ取得
```

| Action | 説明 |
|--------|------|
| `cloud-build` | Cloud Build で非同期ビルドを開始し、完了までポーリング |
| `decide-environment` | タグ・入力値から環境（dev/prod）を決定 |
| `decide-services` | 変更検知・入力値からデプロイ対象サービスを決定 |
| `get-cloud-run-image` | Cloud Run サービスの現在のイメージを取得（フォールバック対応） |

## app-deploy.yml

### フロー

1. **パス検知**: 変更があったサービス（bff, worker）のみビルド対象
2. **Build**: Cloud Build でイメージをビルドし Artifact Registry へ push
3. **Deploy**: Terraform apply で Cloud Run にデプロイ

### トリガーと動作

| トリガー | 環境 | 対象サービス |
|---------|------|-------------|
| main push（app/** 変更） | dev | 変更があったサービスのみ |
| `app-v*` タグ | prod | 全サービス |
| workflow_dispatch | 選択可能 | 選択可能 |

## agent-deploy.yml

ADK エージェントを Vertex AI Agent Engine にデプロイします。
`app/adk/agents/` 配下の全エージェントを自動検出し、並列でデプロイします。

### 実行方法

1. Actions → **Deploy Agent Engine** → **Run workflow**
2. environment を選択（dev / prod）
3. 実行

## 環境の切り替え

| トリガー | 環境 |
|---------|------|
| main push | dev |
| `infra-v*` / `app-v*` タグ | prod |
| workflow_dispatch | 手動選択 |

## GitHub Environment Secrets

各環境（development / production）に以下の secrets を設定：

| Secret | 説明 |
|--------|------|
| `PROJECT_ID` | GCP プロジェクト ID |
| `WORKLOAD_IDENTITY_PROVIDER` | Workload Identity Provider |
| `SERVICE_ACCOUNT` | GitHub Actions 用サービスアカウント |
