# PDF データ抽出 LLM 比較実験

不動産賃貸借契約書のPDFから構造化データを抽出する際に、複数のLLM（Gemini, GPT-4o, Claude, Azure Document Intelligence）を比較評価する実験プロジェクトです。

## 目的

本実験は、PDFの契約書から指定されたJSONスキーマに基づき構造化データを抽出するタスクにおいて、**コスト効率**と**データ抽出精度**の観点から最も優れたLLMソリューションを特定することを目的とします。

## プロジェクト構成

```
llm-experiment/
├── src/                          # ソースコード
│   ├── processors/              # PDF処理モジュール
│   │   ├── pdf_processor.py    # PDF読み込み・検証
│   │   └── image_converter.py  # PDF→画像変換
│   ├── evaluators/              # 評価モジュール
│   │   ├── schema_validator.py    # スキーマ検証
│   │   ├── accuracy_calculator.py # 精度計算
│   │   └── cost_calculator.py     # コスト計算
│   ├── utils/                   # ユーティリティモジュール
│   │   ├── logger.py            # ログ管理
│   │   └── config_loader.py     # 設定読み込み
│   ├── visualizers/             # 可視化モジュール
│   │   └── result_visualizer.py # 結果可視化
│   ├── api_clients/             # API連携（未実装）
│   └── main.py                  # メイン実行スクリプト
├── tests/                        # テストコード
│   ├── test_pdf_processor.py
│   ├── test_image_converter.py
│   ├── test_schema_validator.py
│   ├── test_accuracy_calculator.py
│   ├── test_cost_calculator.py
│   ├── test_logger.py
│   ├── test_config_loader.py
│   └── test_result_visualizer.py
├── config/                       # 設定ファイル
│   ├── pricing.json             # トークン単価設定
│   ├── schema.json              # JSONスキーマ定義
│   └── api_keys.json            # APIキー（.gitignore対象）
├── data/                         # データセット
│   ├── input/                   # 入力PDF（20種類以上）
│   └── golden/                  # 正解データ（Golden Standard）
├── output/                       # 出力ファイル
│   ├── extracted/               # LLM抽出結果
│   ├── logs/                    # 実行ログ
│   ├── results/                 # 評価結果
│   ├── images/                  # PDF変換画像
│   └── visualizations/          # 可視化グラフ
├── example_usage.py              # PDF処理モジュールの使用例
├── example_evaluators.py         # 評価モジュールの使用例
├── example_utils.py              # ユーティリティモジュールの使用例
├── example_visualizer.py         # 可視化モジュールの使用例
├── requirements.txt              # 依存パッケージ
├── 実験手順書.md                    # 実験の詳細手順
├── 実験スクリプト要件定義.md        # システム要件定義
├── PDF処理モジュールREADME.md       # PDF処理の詳細ドキュメント
├── 評価モジュールREADME.md          # 評価モジュールの詳細ドキュメント
├── ユーティリティとメインREADME.md # ユーティリティとメインスクリプトのドキュメント
└── README.md                       # このファイル
```

## セットアップ

### 1. 依存パッケージのインストール

```bash
cd llm-experiment
pip install -r requirements.txt
```

### 2. システム依存パッケージ（Poppler）のインストール

PDF処理には`poppler`が必要です。

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install poppler-utils
```

#### macOS
```bash
brew install poppler
```

#### Windows
[Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/)からダウンロードし、環境変数のPATHに追加してください。

### 3. データセットの準備

```bash
# 入力PDFを配置
cp /path/to/your/contracts/*.pdf data/input/

# 正解データ（Golden Standard）を作成
# data/golden/ に各PDFに対応するJSONファイルを配置
```

### 4. APIキーの設定

```bash
# config/api_keys.json を作成（サンプルは後述）
```

## 使用方法

### PDF処理モジュールの動作確認

```bash
python example_usage.py
```

詳細は [PDF処理モジュールREADME.md](PDF処理モジュールREADME.md) を参照してください。

### 評価モジュールの動作確認

```bash
python example_evaluators.py
```

詳細は [評価モジュールREADME.md](評価モジュールREADME.md) を参照してください。

### ユーティリティモジュールの動作確認

```bash
python example_utils.py
```

詳細は [ユーティリティとメインREADME.md](ユーティリティとメインREADME.md) を参照してください。

### メイン実験スクリプトの実行

```bash
# デフォルト実行（全PDF、モックモデル）
python src/main.py

# 特定のモデルを指定
python src/main.py --models gpt-4o claude-3-sonnet

# 可視化をスキップ
python src/main.py --skip-visualization

# ドライラン（設定確認のみ）
python src/main.py --dry-run
```

詳細は [ユーティリティとメインREADME.md](ユーティリティとメインREADME.md) を参照してください。

### 可視化の実行

```bash
# 可視化モジュールの動作確認
python example_visualizer.py

# 既存の実験結果を可視化
# （output/results/ にサマリーファイルがある場合）
```

実験実行時に自動的に可視化が生成されます。出力先: `output/visualizations/`

### テストの実行

```bash
# すべてのテストを実行
pytest tests/ -v

# カバレッジ付き
pytest tests/ --cov=src --cov-report=html
```

## 実装状況

### 完了
- ✅ PDF処理モジュール（PDFProcessor, ImageConverter）
- ✅ 評価モジュール（SchemaValidator, AccuracyCalculator, CostCalculator）
- ✅ ユーティリティモジュール（ExperimentLogger, ConfigLoader）
- ✅ 可視化モジュール（ResultVisualizer）
- ✅ メイン実行スクリプト（main.py）
- ✅ JSONスキーマ定義（config/schema.json）
- ✅ テストコード
- ✅ 使用例スクリプト
- ✅ ドキュメント
- ✅ API連携モジュールのテンプレート（BaseLLMClient, テンプレートファイル）

### 要実装
- ⏳ API連携モジュールの具体的実装（Gemini, GPT-4o, Claude, Azure）
  - テンプレートファイルが `src/api_clients/` に用意されています
  - 詳細は [API連携モジュール実装ガイド.md](API連携モジュール実装ガイド.md) を参照してください

## 評価指標

本実験では以下の指標でLLMを評価します。

| 評価指標 | 定義 |
|---------|------|
| **項目正答率** | 正解JSONの総フィールド数に対し、正しく抽出されたフィールドの割合 |
| **F1スコア** | 各キー・バリューペアを要素とみなし、適合率と再現率から算出 |
| **完全一致率** | LLMの出力JSONが正解JSONと文字列として完全に一致した割合 |
| **スキーマ準拠率** | 出力JSONが定義されたスキーマを満たしている割合 |
| **平均コスト/PDF** | 1つのPDFの抽出にかかった平均費用（円） |
| **平均応答時間** | APIリクエスト送信からレスポンス取得までの平均時間（秒） |

## 比較対象モデル

| モデル | 提供元 | 備考 |
|-------|--------|------|
| Gemini Pro 2.5 / Flash 2.5 | Google | マルチモーダル入力 |
| GPT-4o | OpenAI | マルチモーダル入力 |
| Claude 3 Opus / Sonnet | Anthropic | マルチモーダル入力 |
| Azure Document Intelligence | Microsoft Azure | 特化型サービス（ベンチマーク） |

## 設定ファイルの例

### config/api_keys.json（サンプル）

```json
{
  "gemini": "YOUR_GEMINI_API_KEY",
  "openai": "YOUR_OPENAI_API_KEY",
  "anthropic": "YOUR_ANTHROPIC_API_KEY",
  "azure": {
    "endpoint": "YOUR_AZURE_ENDPOINT",
    "key": "YOUR_AZURE_KEY"
  }
}
```

**注意:** このファイルは`.gitignore`に追加してください。

### config/pricing.json

トークン単価はすでに設定済みです。最新の価格に更新する場合は、このファイルを編集してください。

## API連携モジュールの実装

API連携モジュールのテンプレートが用意されています。各担当者は以下のファイルを編集して実装してください：

### テンプレートファイル

- `src/api_clients/gemini_client.py` - Gemini API クライアント
- `src/api_clients/gpt_client.py` - OpenAI GPT API クライアント
- `src/api_clients/claude_client.py` - Anthropic Claude API クライアント
- `src/api_clients/azure_client.py` - Azure Document Intelligence クライアント

### 実装方法

詳細な実装ガイドは **[API連携モジュール実装ガイド.md](API連携モジュール実装ガイド.md)** を参照してください。

**主な実装手順:**

1. 必要なライブラリをインストール（`pip install google-generativeai` など）
2. SDK の初期化を実装（`__init__` メソッド）
3. `extract_data_from_pdf()` メソッドを実装
4. プロンプト/メッセージ構築メソッドを実装
5. API呼び出しメソッドを実装
6. トークン使用量の記録を実装
7. テストを作成して動作確認

各ファイルには `TODO` コメントが記載されており、実装が必要な箇所が明示されています。

### テストテンプレート

`tests/test_api_client_template.py` にテストのテンプレートが用意されています。
このファイルをコピーして `test_<client_name>.py` を作成してください。

## ドキュメント

詳細なドキュメントは以下を参照してください：

- **[実験手順書.md](実験手順書.md)** - 実験の全体フロー
- **[実験スクリプト要件定義.md](実験スクリプト要件定義.md)** - システムの詳細要件
- **[PDF処理モジュールREADME.md](PDF処理モジュールREADME.md)** - PDF処理の使い方
- **[評価モジュールREADME.md](評価モジュールREADME.md)** - 評価機能の使い方
- **[ユーティリティとメインREADME.md](ユーティリティとメインREADME.md)** - ユーティリティとメインスクリプトの使い方
- **[API連携モジュール実装ガイド.md](API連携モジュール実装ガイド.md)** - API連携モジュールの実装方法

## 開発

### ディレクトリ構成の説明

- **src/processors/**: PDFファイルの読み込み、画像変換を担当
- **src/evaluators/**: スキーマ検証、精度計算、コスト計算を担当
- **src/api_clients/**: 各LLM APIとの通信を担当（未実装）
- **src/utils/**: ログ管理、設定読み込みなどのユーティリティ（未実装）
- **tests/**: 各モジュールのユニットテスト
- **config/**: 設定ファイル（APIキー、価格設定、スキーマ）
- **data/**: 入力PDF と正解データ
- **output/**: 実行結果の出力先

### コーディング規約

- Python 3.8以上
- PEP 8に準拠
- 型ヒントを使用
- docstringを記述
- ログ出力を適切に使用

## トラブルシューティング

### Popplerが見つからない

```
PDFInfoNotInstalledError: Unable to get page count. Is poppler installed and in PATH?
```

→ Popplerをインストールし、PATHに追加してください（セットアップセクション参照）

### テストが失敗する

サンプルPDFがない場合、一部のテストはスキップされます。テストを完全に実行するには、`data/input/sample.pdf` を配置してください。

### ImportError

```python
sys.path.insert(0, str(Path(__file__).parent))
```

スクリプトを実行する際は、`llm-experiment/`ディレクトリから実行してください。

## ライセンス

このプロジェクトは実験用です。

## 連絡先

質問や問題がある場合は、Issueを作成してください。
