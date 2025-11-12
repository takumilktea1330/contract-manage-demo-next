# 評価モジュール

LLMの抽出結果を評価するための3つのモジュールを提供します。

## 機能

### SchemaValidator
- JSONスキーマに基づく検証
- スキーマ準拠率の計算
- バッチ検証
- 詳細なエラーレポート

### AccuracyCalculator
- 項目正答率の計算
- F1スコアの計算（適合率・再現率）
- 完全一致判定
- ネストされたデータの比較
- 詳細な差分レポート

### CostCalculator
- トークン数からのコスト計算
- 複数通貨対応（USD, JPY）
- 平均コスト/PDFの算出
- モデル間コスト比較
- コストレポートの出力

## インストール

```bash
pip install -r requirements.txt
```

主要なパッケージ:
- `jsonschema`: スキーマ検証

## 使用方法

### SchemaValidator

#### 基本的な使い方

```python
from src.evaluators import SchemaValidator

# スキーマの定義
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["name", "age"]
}

# バリデータの初期化
validator = SchemaValidator(schema)

# データの検証
data = {"name": "田中太郎", "age": 30, "email": "tanaka@example.com"}
is_valid, errors = validator.validate(data)

if is_valid:
    print("データは有効です")
else:
    print(f"エラー: {errors}")
```

#### ファイルからスキーマを読み込む

```python
# JSONファイルからスキーマを読み込む
validator = SchemaValidator("config/schema.json")

# JSONファイルを検証
is_valid, errors = validator.validate_file("output/extracted/result.json")
```

#### バッチ検証

```python
# 複数のデータを一括検証
data_list = [data1, data2, data3, data4, data5]
results = validator.validate_batch(data_list)

# スキーマ準拠率を計算
conformance_rate = validator.calculate_conformance_rate(results)
print(f"スキーマ準拠率: {conformance_rate:.2%}")
```

#### 詳細な検証結果

```python
# 詳細な検証結果を取得
result = validator.validate_with_details(data)
print(f"エラー数: {result['error_count']}")
print(f"エラー詳細: {result['errors']}")
```

### AccuracyCalculator

#### 基本的な使い方

```python
from src.evaluators import AccuracyCalculator

# 正解データと抽出データ
golden_data = {
    "name": "田中太郎",
    "age": 30,
    "address": {"city": "東京都", "zip": "100-0001"}
}

extracted_data = {
    "name": "田中太郎",
    "age": 31,  # 誤り
    "address": {"city": "東京都", "zip": "100-0001"}
}

# AccuracyCalculatorの初期化
calculator = AccuracyCalculator(golden_data, extracted_data)

# 各種評価指標の計算
field_accuracy = calculator.calculate_field_accuracy()
f1_score = calculator.calculate_f1_score()
exact_match = calculator.calculate_exact_match()

print(f"項目正答率: {field_accuracy:.2%}")
print(f"F1スコア: {f1_score:.4f}")
print(f"完全一致: {exact_match}")
```

#### JSONファイルから読み込む

```python
# ファイルパスを直接指定
calculator = AccuracyCalculator(
    golden_data="data/golden/contract_01.json",
    extracted_data="output/extracted/contract_01.json"
)
```

#### 全メトリクスの一括取得

```python
# 全ての評価指標を一度に取得
metrics = calculator.get_metrics()

print(f"項目正答率: {metrics['field_accuracy']:.2%}")
print(f"F1スコア: {metrics['f1_score']:.4f}")
print(f"完全一致: {metrics['exact_match']}")
print(f"統計情報: {metrics['statistics']}")
```

#### 詳細な差分情報

```python
# 詳細な差分を取得
diff = calculator.get_detailed_diff()

print(f"正解フィールド: {len(diff['correct'])}")
print(f"不正解フィールド: {len(diff['incorrect'])}")
print(f"不足フィールド: {len(diff['missing'])}")
print(f"余分フィールド: {len(diff['extra'])}")

# 不正解フィールドの詳細
for item in diff['incorrect']:
    print(f"パス: {item['path']}")
    print(f"  正解: {item['golden_value']}")
    print(f"  抽出: {item['extracted_value']}")
```

#### 差分レポートの出力

```python
# 差分レポートをJSONファイルとして出力
calculator.export_diff_report("output/reports/diff_report.json")
```

### CostCalculator

#### 基本的な使い方

```python
from src.evaluators import CostCalculator

# 価格設定を読み込む
calculator = CostCalculator("config/pricing.json")

# コスト計算
model = "gpt-4o"
input_tokens = 10_000
output_tokens = 3_000

cost_jpy = calculator.calculate_cost(
    model=model,
    input_tokens=input_tokens,
    output_tokens=output_tokens,
    currency="JPY"
)

print(f"コスト: {cost_jpy:.2f}円")
```

#### 辞書形式の価格設定

```python
# 価格設定を辞書で渡す
pricing_config = {
    "gpt-4o": {
        "input_token_price_per_1m": 2.5,
        "output_token_price_per_1m": 10.0,
        "currency": "USD",
        "exchange_rate": 150.0
    }
}

calculator = CostCalculator(pricing_config)
```

#### コスト内訳の取得

```python
# 詳細なコスト内訳を取得
breakdown = calculator.calculate_cost_breakdown(
    model="gpt-4o",
    input_tokens=10_000,
    output_tokens=3_000,
    currency="JPY"
)

print(f"入力コスト: {breakdown['input_cost']:.2f}円")
print(f"出力コスト: {breakdown['output_cost']:.2f}円")
print(f"合計コスト: {breakdown['total_cost']:.2f}円")
print(f"合計トークン: {breakdown['total_tokens']:,}")
```

#### 平均コストの計算

```python
# 複数のAPIコール結果から平均コストを計算
results = [
    {"model": "gpt-4o", "input_tokens": 10_000, "output_tokens": 3_000},
    {"model": "gpt-4o", "input_tokens": 15_000, "output_tokens": 4_000},
    {"model": "gpt-4o", "input_tokens": 12_000, "output_tokens": 3_500}
]

average_cost = calculator.calculate_average_cost(results, currency="JPY")
print(f"平均コスト/PDF: {average_cost:.2f}円")
```

#### コストサマリーの取得

```python
# 統計情報を含むサマリーを取得
summary = calculator.get_cost_summary(results, currency="JPY")

print(f"合計コスト: {summary['total_cost']:.2f}円")
print(f"平均コスト: {summary['average_cost']:.2f}円")
print(f"最小コスト: {summary['min_cost']:.2f}円")
print(f"最大コスト: {summary['max_cost']:.2f}円")
print(f"処理件数: {summary['count']}件")
print(f"合計トークン: {summary['total_tokens']:,}")
```

#### モデル間のコスト比較

```python
# 複数モデルのコストを比較（安い順にソート）
costs = calculator.compare_models(
    input_tokens=10_000,
    output_tokens=3_000,
    currency="JPY"
)

for model_name, cost in costs.items():
    print(f"{model_name}: {cost:.2f}円")
```

#### コストレポートの出力

```python
# コストレポートをJSONファイルとして出力
calculator.export_cost_report(
    results=results,
    output_path="output/reports/cost_report.json",
    currency="JPY"
)
```

## 設定ファイル

### pricing.json

価格設定ファイルの形式:

```json
{
  "model-name": {
    "input_token_price_per_1m": 2.5,
    "output_token_price_per_1m": 10.0,
    "currency": "USD",
    "exchange_rate": 150.0,
    "note": "モデルの説明（オプション）"
  }
}
```

- `input_token_price_per_1m`: 入力トークン100万あたりの価格
- `output_token_price_per_1m`: 出力トークン100万あたりの価格
- `currency`: 価格の通貨（USDまたはJPY）
- `exchange_rate`: 為替レート（USD→JPY）

## テスト

### テストの実行

```bash
# すべてのテストを実行
pytest tests/ -v

# 特定のモジュールのテストを実行
pytest tests/test_schema_validator.py -v
pytest tests/test_accuracy_calculator.py -v
pytest tests/test_cost_calculator.py -v

# カバレッジを含めて実行
pytest tests/ --cov=src/evaluators --cov-report=html
```

## 使用例スクリプト

`example_evaluators.py`を実行すると、3つのモジュール全ての使用例を確認できます。

```bash
python example_evaluators.py
```

## 実験での使用

### 実験フローでの統合例

```python
from src.evaluators import SchemaValidator, AccuracyCalculator, CostCalculator

# 1. スキーマ検証
schema_validator = SchemaValidator("config/schema.json")
is_valid, errors = schema_validator.validate(extracted_data)

# 2. 精度評価
accuracy_calc = AccuracyCalculator(golden_data, extracted_data)
metrics = accuracy_calc.get_metrics()

# 3. コスト計算
cost_calc = CostCalculator("config/pricing.json")
cost = cost_calc.calculate_cost(model, input_tokens, output_tokens, "JPY")

# 4. 結果の記録
result = {
    "pdf_name": "contract_01.pdf",
    "model": model,
    "schema_valid": is_valid,
    "field_accuracy": metrics['field_accuracy'],
    "f1_score": metrics['f1_score'],
    "exact_match": metrics['exact_match'],
    "cost_jpy": cost,
    "input_tokens": input_tokens,
    "output_tokens": output_tokens
}
```

## 評価指標の詳細

### 項目正答率

正解JSONの総フィールド数に対し、正しく抽出されたフィールドの割合。

```
項目正答率 = 正しく抽出されたフィールド数 / 総フィールド数
```

### F1スコア

適合率（Precision）と再現率（Recall）の調和平均。

```
Precision = TP / (TP + FP)
Recall = TP / (TP + FN)
F1 = 2 * (Precision * Recall) / (Precision + Recall)
```

- TP (True Positive): 正しく抽出されたフィールド
- FP (False Positive): 余分なフィールド
- FN (False Negative): 不足しているフィールド

### 完全一致率

LLMの出力JSONが正解JSONと文字列として完全に一致するか。

### スキーマ準拠率

出力JSONが定義されたスキーマを満たしている割合。

```
スキーマ準拠率 = 有効なJSON数 / 総JSON数
```

## トラブルシューティング

### スキーマ検証エラー

**症状:** スキーマ検証で予期しないエラーが発生

**解決方法:**
1. スキーマファイルのJSON形式が正しいか確認
2. スキーマが[JSON Schema Draft 7](https://json-schema.org/draft-07/json-schema-release-notes.html)に準拠しているか確認
3. データ型の定義が正しいか確認

### 精度計算で0%になる

**症状:** 明らかに一致しているのに精度が0%

**解決方法:**
1. データ型が一致しているか確認（文字列vs数値など）
2. 空白やフォーマットの違いを確認
3. `tolerance`パラメータを調整（数値比較用）

### コスト計算エラー

**症状:** モデルが見つからないエラー

**解決方法:**
1. `pricing.json`にモデルの設定が存在するか確認
2. モデル名のスペルミスを確認
3. 必須フィールド（`input_token_price_per_1m`、`output_token_price_per_1m`）が設定されているか確認

## パフォーマンス

### 大量データの処理

大量のJSONを処理する場合のベストプラクティス:

```python
# バッチ処理
results = []
for golden_path, extracted_path in zip(golden_files, extracted_files):
    calculator = AccuracyCalculator(golden_path, extracted_path)
    metrics = calculator.get_metrics()
    results.append(metrics)

    # メモリ解放
    del calculator
```

### キャッシュの活用

`AccuracyCalculator`は比較結果をキャッシュします。同じインスタンスで複数の評価指標を計算する場合、再計算は行われません。

```python
calculator = AccuracyCalculator(golden, extracted)

# 最初の計算（比較処理が実行される）
accuracy = calculator.calculate_field_accuracy()

# 2回目以降（キャッシュを使用）
f1_score = calculator.calculate_f1_score()
metrics = calculator.get_metrics()
```

## ライセンス

このプロジェクトは実験用です。

## 関連ドキュメント

- [実験手順書.md](実験手順書.md) - 実験全体の計画
- [実験スクリプト要件定義.md](実験スクリプト要件定義.md) - システム全体の要件
- [PDF処理モジュールREADME.md](PDF処理モジュールREADME.md) - PDF処理モジュールのドキュメント
