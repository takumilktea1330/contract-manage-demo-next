# ユーティリティモジュールとメイン実行スクリプト

実験の実行管理、ログ記録、設定読み込みを行うモジュールとメイン実行スクリプトです。

## 機能

### ExperimentLogger
- 実験セッションの管理
- APIリクエスト/レスポンスのログ記録
- 評価結果のログ記録
- エラーログの記録
- CSV/JSONへの出力
- サマリーレポート生成

### ConfigLoader
- APIキーの読み込み（ファイルまたは環境変数）
- 価格設定の読み込み
- JSONスキーマの読み込み
- システムプロンプトの読み込み
- 設定の検証

### メイン実行スクリプト (main.py)
- 実験の一括実行
- PDF処理とLLM連携
- 評価とログ記録
- 結果の集計と出力

## インストール

```bash
cd llm-experiment
pip install -r requirements.txt
```

## 使用方法

### ExperimentLogger

#### 基本的な使い方

```python
from src.utils import ExperimentLogger

# ロガーの初期化
logger = ExperimentLogger(log_dir="output/logs")

# リクエストログ
logger.log_request("gpt-4o", "contract_01.pdf")

# レスポンスログ
tokens = {"input_tokens": 10000, "output_tokens": 3000}
logger.log_response(
    model="gpt-4o",
    pdf_name="contract_01.pdf",
    response_time=2.5,
    tokens=tokens,
    success=True
)

# 評価ログ
metrics = {
    "field_accuracy": 0.95,
    "f1_score": 0.92,
    "exact_match": False,
    "schema_valid": True
}
logger.log_evaluation("gpt-4o", "contract_01.pdf", metrics, cost=187.5)

# エラーログ
try:
    # 何か処理
    pass
except Exception as e:
    logger.log_error("gpt-4o", "contract_01.pdf", e, "api_error")
```

#### 結果の保存

```python
# CSVに保存
csv_path = logger.save_to_csv("output/results/metrics.csv")

# サマリーレポート保存
summary_path = logger.save_summary_report("output/results/summary.json")

# サマリー表示
logger.print_summary()
```

#### 統計情報の取得

```python
# 実行統計
stats = logger.get_statistics()
print(f"総リクエスト: {stats['total_requests']}")
print(f"成功率: {stats['success_rate']:.2%}")

# サマリーレポート
summary = logger.generate_summary_report()
for model, data in summary['models'].items():
    print(f"{model}: 正答率={data['avg_field_accuracy']:.2%}")
```

### ConfigLoader

#### 基本的な使い方

```python
from src.utils import ConfigLoader

# ConfigLoaderの初期化
config_loader = ConfigLoader(config_dir="config")

# APIキーの読み込み
api_keys = config_loader.load_api_keys()
gemini_key = api_keys['gemini']

# 価格設定の読み込み
pricing = config_loader.load_pricing()

# JSONスキーマの読み込み
schema = config_loader.load_schema()

# システムプロンプトの読み込み
prompt = config_loader.load_system_prompt()
```

#### 環境変数からの読み込み

APIキーファイルが存在しない場合、環境変数から自動的に読み込みます。

```bash
# 環境変数の設定
export GEMINI_API_KEY="your_gemini_key"
export OPENAI_API_KEY="your_openai_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
export AZURE_ENDPOINT="your_azure_endpoint"
export AZURE_KEY="your_azure_key"
```

または`.env`ファイルを作成:

```
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

#### 設定の検証

```python
# 設定の妥当性を検証
is_valid = config_loader.validate_config()
if is_valid:
    print("すべての設定が有効です")
```

#### 全設定の一括取得

```python
# すべての設定を一度に取得
configs = config_loader.get_all_configs()

api_keys = configs['api_keys']
pricing = configs['pricing']
schema = configs['schema']
system_prompt = configs['system_prompt']
```

### メイン実行スクリプト

#### 基本的な実行

```bash
# デフォルト実行（全PDF、モックモデル）
python src/main.py

# 特定のモデルを指定
python src/main.py --models gpt-4o claude-3-sonnet gemini-2.5-pro

# 特定のPDFのみ処理
python src/main.py --pdf contract_01.pdf

# パターン指定
python src/main.py --pdf "contract_*.pdf"

# 評価をスキップ
python src/main.py --skip-evaluation

# ドライラン（設定確認のみ）
python src/main.py --dry-run
```

#### カスタムディレクトリ指定

```bash
python src/main.py \
  --config-dir /path/to/config \
  --data-dir /path/to/data \
  --output-dir /path/to/output
```

#### コマンドラインオプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `--models` | 実行するモデル（スペース区切り） | mock-model |
| `--pdf` | 処理するPDFファイル（パターン可） | *.pdf |
| `--skip-evaluation` | 評価をスキップ | False |
| `--config-dir` | 設定ディレクトリ | config |
| `--data-dir` | データディレクトリ | data |
| `--output-dir` | 出力ディレクトリ | output |
| `--dry-run` | ドライラン（設定確認のみ） | False |

### プログラムからの実行

```python
from src.main import ExperimentRunner

# 実験ランナーの初期化
runner = ExperimentRunner(
    config_dir="config",
    data_dir="data",
    output_dir="output"
)

# 実験実行
runner.run_experiment(
    models=["gpt-4o", "claude-3-sonnet"],
    pdf_pattern="contract_*.pdf",
    skip_evaluation=False
)
```

## 出力ファイル

### ログファイル

```
output/logs/
├── experiment_YYYYMMDD_HHMMSS.log  # 実験ログ
```

### 結果ファイル

```
output/results/
├── metrics_YYYYMMDD_HHMMSS.csv      # 評価メトリクス（CSV）
└── summary_YYYYMMDD_HHMMSS.json     # サマリーレポート（JSON）
```

### 抽出データ

```
output/extracted/
├── gpt-4o_contract_01.json
├── claude-3-sonnet_contract_01.json
└── ...
```

## 出力形式

### metrics.csv

```csv
timestamp,model,pdf_name,field_accuracy,f1_score,exact_match,schema_valid,cost_jpy,response_time,input_tokens,output_tokens,total_tokens
2024-01-15T10:30:45,gpt-4o,contract_01,0.95,0.92,False,True,187.5,2.5,10000,3000,13000
```

### summary.json

```json
{
  "session_id": "20240115_103045",
  "session_start": "2024-01-15T10:30:45",
  "session_end": "2024-01-15T11:45:30",
  "total_evaluations": 20,
  "total_errors": 0,
  "models": {
    "gpt-4o": {
      "count": 10,
      "avg_field_accuracy": 0.93,
      "avg_f1_score": 0.90,
      "exact_match_rate": 0.10,
      "schema_conformance_rate": 0.95,
      "avg_cost_per_pdf": 185.5,
      "total_cost": 1855.0,
      "avg_response_time": 2.45,
      "total_tokens": 130000
    }
  }
}
```

## 設定ファイル

### config/api_keys.json

```json
{
  "gemini": "YOUR_GEMINI_API_KEY",
  "openai": "YOUR_OPENAI_API_KEY",
  "anthropic": "YOUR_ANTHROPIC_API_KEY",
  "azure": {
    "endpoint": "https://YOUR_RESOURCE.cognitiveservices.azure.com/",
    "key": "YOUR_AZURE_KEY"
  }
}
```

**注意:** このファイルは`.gitignore`に追加してください。

### config/pricing.json

すでに設定済み。最新の価格に更新する場合は編集してください。

### prompts/system_prompt.txt（オプション）

```
あなたは不動産賃貸借契約書からデータを抽出する専門家です。
提供された契約書PDFから、指定されたJSONスキーマに従って正確にデータを抽出してください。

重要な注意事項:
1. 情報が明示的に記載されている場合のみ抽出してください
2. 推測や仮定で情報を補完しないでください
...
```

## テスト

### テストの実行

```bash
# ユーティリティモジュールのテスト
pytest tests/test_logger.py -v
pytest tests/test_config_loader.py -v

# すべてのテスト
pytest tests/ -v

# カバレッジ付き
pytest tests/ --cov=src/utils --cov-report=html
```

## 使用例スクリプト

`example_utils.py`を実行すると、ExperimentLoggerとConfigLoaderの使用例を確認できます。

```bash
python example_utils.py
```

## 実験フローの例

```python
from src.main import ExperimentRunner

# 1. 実験ランナー初期化
runner = ExperimentRunner()

# 2. PDFリスト取得
pdf_files = runner.get_pdf_list("contract_*.pdf")
print(f"処理対象: {len(pdf_files)}件")

# 3. 各PDFに対して実行
for pdf_path in pdf_files:
    for model in ["gpt-4o", "claude-3-sonnet"]:
        # 抽出
        result = runner.run_extraction(pdf_path, model)

        if result:
            # 評価
            eval_result = runner.run_evaluation(
                pdf_path.stem,
                model,
                result['extracted_data'],
                result['tokens']
            )

# 4. 結果保存
runner.logger.save_to_csv()
runner.logger.save_summary_report()
runner.logger.print_summary()
```

## トラブルシューティング

### APIキーが見つからない

```
FileNotFoundError: APIキーファイルが見つからず、環境変数も設定されていません
```

**解決方法:**
1. `config/api_keys.json`を作成
2. または環境変数を設定（`GEMINI_API_KEY`等）
3. または`.env`ファイルを作成

### 価格設定が見つからない

```
FileNotFoundError: 価格設定ファイルが見つかりません
```

**解決方法:**
`config/pricing.json`が存在することを確認してください。

### PDFが見つからない

```
処理対象のPDFが見つかりません
```

**解決方法:**
1. `data/input/`にPDFファイルを配置
2. `--pdf`オプションで正しいパスを指定

### 正解データがない

正解データがない場合、評価はスキップされますが、抽出は実行されます。

```bash
# 評価をスキップして実行
python src/main.py --skip-evaluation
```

## カスタマイズ

### カスタムロガー

```python
class CustomLogger(ExperimentLogger):
    def log_custom_metric(self, model, pdf_name, metric_name, value):
        # カスタムメトリクスを記録
        pass
```

### カスタム設定ローダー

```python
class CustomConfigLoader(ConfigLoader):
    def load_custom_config(self, file_name):
        # カスタム設定を読み込む
        pass
```

## パフォーマンス

### 並列実行

現在の実装は逐次処理ですが、将来的に並列実行を追加予定です。

### メモリ管理

大量のPDFを処理する場合、適宜ログを保存してメモリを解放してください。

```python
# 10件ごとに保存
if len(logger.evaluation_logs) % 10 == 0:
    logger.save_to_csv()
```

## ライセンス

このプロジェクトは実験用です。

## 関連ドキュメント

- [README.md](README.md) - プロジェクト全体の説明
- [実験手順書.md](実験手順書.md) - 実験の詳細手順
- [PDF処理モジュールREADME.md](PDF処理モジュールREADME.md) - PDF処理
- [評価モジュールREADME.md](評価モジュールREADME.md) - 評価機能
