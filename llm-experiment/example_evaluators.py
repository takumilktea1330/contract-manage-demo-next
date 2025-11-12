"""
評価モジュールの使用例

このスクリプトは、SchemaValidator、AccuracyCalculator、CostCalculatorの
基本的な使い方を示します。
"""

import sys
import json
import logging
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.evaluators import SchemaValidator, AccuracyCalculator, CostCalculator

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_schema_validator():
    """SchemaValidatorの使用例"""
    logger.info("=" * 60)
    logger.info("SchemaValidator の使用例")
    logger.info("=" * 60)

    # 1. スキーマの定義
    logger.info("\n1. JSONスキーマの定義")
    schema = {
        "type": "object",
        "properties": {
            "contract_type": {"type": "string"},
            "contract_date": {"type": "string", "format": "date"},
            "parties": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "role": {"type": "string"}
                    },
                    "required": ["name", "role"]
                }
            },
            "rent": {"type": "number", "minimum": 0}
        },
        "required": ["contract_type", "contract_date", "rent"]
    }
    logger.info("✓ スキーマを定義しました")

    # 2. バリデータの初期化
    logger.info("\n2. SchemaValidatorの初期化")
    validator = SchemaValidator(schema)
    logger.info("✓ バリデータを初期化しました")

    # 3. 正常なデータの検証
    logger.info("\n3. 正常なデータの検証")
    valid_data = {
        "contract_type": "普通賃貸借契約",
        "contract_date": "2024-01-01",
        "parties": [
            {"name": "田中太郎", "role": "貸主"},
            {"name": "佐藤花子", "role": "借主"}
        ],
        "rent": 100000
    }

    is_valid, errors = validator.validate(valid_data)
    if is_valid:
        logger.info("✓ データは有効です")
    else:
        logger.error(f"✗ データは無効です: {errors}")

    # 4. 無効なデータの検証
    logger.info("\n4. 無効なデータの検証")
    invalid_data = {
        "contract_type": "普通賃貸借契約",
        # contract_date が欠落
        "parties": [
            {"name": "田中太郎"}  # role が欠落
        ],
        "rent": -50000  # 負の値（最小値制約違反）
    }

    is_valid, errors = validator.validate(invalid_data)
    if is_valid:
        logger.info("✓ データは有効です")
    else:
        logger.warning(f"✗ データは無効です:")
        for error in errors:
            logger.warning(f"  - {error}")

    # 5. バッチ検証
    logger.info("\n5. バッチ検証")
    data_list = [valid_data, invalid_data, valid_data]
    results = validator.validate_batch(data_list)

    conformance_rate = validator.calculate_conformance_rate(results)
    logger.info(f"✓ スキーマ準拠率: {conformance_rate:.2%}")


def example_accuracy_calculator():
    """AccuracyCalculatorの使用例"""
    logger.info("\n" + "=" * 60)
    logger.info("AccuracyCalculator の使用例")
    logger.info("=" * 60)

    # 1. 正解データと抽出データの定義
    logger.info("\n1. データの定義")
    golden_data = {
        "contract_type": "普通賃貸借契約",
        "contract_date": "2024-01-01",
        "rent": 100000,
        "deposit": 200000,
        "parties": [
            {"name": "田中太郎", "role": "貸主"},
            {"name": "佐藤花子", "role": "借主"}
        ],
        "address": {
            "pref": "東京都",
            "city": "渋谷区",
            "building": "テストビル101"
        }
    }

    extracted_data = {
        "contract_type": "普通賃貸借契約",
        "contract_date": "2024-01-01",
        "rent": 100000,
        "deposit": 300000,  # 誤り
        "parties": [
            {"name": "田中太郎", "role": "貸主"},
            {"name": "佐藤花子", "role": "借主"}
        ],
        "address": {
            "pref": "東京都",
            "city": "新宿区",  # 誤り
            "building": "テストビル101"
        }
    }

    logger.info("✓ 正解データと抽出データを定義しました")

    # 2. AccuracyCalculatorの初期化
    logger.info("\n2. AccuracyCalculatorの初期化")
    calculator = AccuracyCalculator(golden_data, extracted_data)
    logger.info("✓ AccuracyCalculatorを初期化しました")

    # 3. 各種評価指標の計算
    logger.info("\n3. 評価指標の計算")

    field_accuracy = calculator.calculate_field_accuracy()
    logger.info(f"  項目正答率: {field_accuracy:.2%}")

    f1_score = calculator.calculate_f1_score()
    logger.info(f"  F1スコア: {f1_score:.4f}")

    exact_match = calculator.calculate_exact_match()
    logger.info(f"  完全一致: {exact_match}")

    # 4. 詳細な差分情報の取得
    logger.info("\n4. 詳細な差分情報")
    diff = calculator.get_detailed_diff()

    logger.info(f"  正解フィールド数: {len(diff['correct'])}")
    logger.info(f"  不正解フィールド数: {len(diff['incorrect'])}")
    logger.info(f"  不足フィールド数: {len(diff['missing'])}")
    logger.info(f"  余分フィールド数: {len(diff['extra'])}")

    if diff['incorrect']:
        logger.info("\n  不正解フィールドの詳細:")
        for item in diff['incorrect'][:3]:  # 最初の3件のみ表示
            logger.info(f"    - {item['path']}")
            logger.info(f"      正解: {item['golden_value']}")
            logger.info(f"      抽出: {item['extracted_value']}")

    # 5. 全メトリクスの一括取得
    logger.info("\n5. 全メトリクスの一括取得")
    metrics = calculator.get_metrics()
    logger.info(f"  全メトリクス:")
    logger.info(f"    - 項目正答率: {metrics['field_accuracy']:.2%}")
    logger.info(f"    - F1スコア: {metrics['f1_score']:.4f}")
    logger.info(f"    - 完全一致: {metrics['exact_match']}")


def example_cost_calculator():
    """CostCalculatorの使用例"""
    logger.info("\n" + "=" * 60)
    logger.info("CostCalculator の使用例")
    logger.info("=" * 60)

    # 1. 価格設定の読み込み
    logger.info("\n1. 価格設定の読み込み")
    pricing_config_path = Path(__file__).parent / "config" / "pricing.json"

    if pricing_config_path.exists():
        calculator = CostCalculator(pricing_config_path)
        logger.info(f"✓ 価格設定を読み込みました: {pricing_config_path}")
    else:
        logger.warning(f"価格設定ファイルが見つかりません: {pricing_config_path}")
        logger.info("サンプル価格設定を使用します")

        # サンプル価格設定
        pricing_config = {
            "gpt-4o": {
                "input_token_price_per_1m": 2.5,
                "output_token_price_per_1m": 10.0,
                "currency": "USD",
                "exchange_rate": 150.0
            },
            "claude-3.5-sonnet": {
                "input_token_price_per_1m": 3.0,
                "output_token_price_per_1m": 15.0,
                "currency": "USD",
                "exchange_rate": 150.0
            }
        }
        calculator = CostCalculator(pricing_config)
        logger.info("✓ サンプル価格設定を使用します")

    # 2. 単一APIコールのコスト計算
    logger.info("\n2. 単一APIコールのコスト計算")
    model = "gpt-4o"
    input_tokens = 10_000
    output_tokens = 3_000

    cost_usd = calculator.calculate_cost(model, input_tokens, output_tokens, currency="USD")
    cost_jpy = calculator.calculate_cost(model, input_tokens, output_tokens, currency="JPY")

    logger.info(f"  モデル: {model}")
    logger.info(f"  入力トークン: {input_tokens:,}")
    logger.info(f"  出力トークン: {output_tokens:,}")
    logger.info(f"  コスト: ${cost_usd:.4f} / {cost_jpy:.2f}円")

    # 3. コスト内訳の取得
    logger.info("\n3. コスト内訳の取得")
    breakdown = calculator.calculate_cost_breakdown(model, input_tokens, output_tokens, currency="JPY")

    logger.info(f"  入力コスト: {breakdown['input_cost']:.2f}円")
    logger.info(f"  出力コスト: {breakdown['output_cost']:.2f}円")
    logger.info(f"  合計コスト: {breakdown['total_cost']:.2f}円")

    # 4. 複数APIコールの平均コスト計算
    logger.info("\n4. 複数APIコールの平均コスト計算")
    results = [
        {"model": "gpt-4o", "input_tokens": 10_000, "output_tokens": 3_000},
        {"model": "gpt-4o", "input_tokens": 15_000, "output_tokens": 4_000},
        {"model": "gpt-4o", "input_tokens": 12_000, "output_tokens": 3_500},
    ]

    average_cost = calculator.calculate_average_cost(results, currency="JPY")
    logger.info(f"  平均コスト/PDF: {average_cost:.2f}円")

    # 5. コストサマリーの取得
    logger.info("\n5. コストサマリーの取得")
    summary = calculator.get_cost_summary(results, currency="JPY")

    logger.info(f"  合計コスト: {summary['total_cost']:.2f}円")
    logger.info(f"  平均コスト: {summary['average_cost']:.2f}円")
    logger.info(f"  最小コスト: {summary['min_cost']:.2f}円")
    logger.info(f"  最大コスト: {summary['max_cost']:.2f}円")
    logger.info(f"  処理件数: {summary['count']}件")

    # 6. モデル間のコスト比較
    logger.info("\n6. モデル間のコスト比較")
    costs = calculator.compare_models(
        input_tokens=10_000,
        output_tokens=3_000,
        currency="JPY"
    )

    logger.info("  モデル別コスト（安い順）:")
    for model_name, cost in costs.items():
        logger.info(f"    - {model_name}: {cost:.2f}円")


def main():
    """メイン関数"""
    logger.info("評価モジュールの使用例を実行します\n")

    # SchemaValidatorの使用例
    example_schema_validator()

    # AccuracyCalculatorの使用例
    example_accuracy_calculator()

    # CostCalculatorの使用例
    example_cost_calculator()

    logger.info("\n" + "=" * 60)
    logger.info("使用例の実行が完了しました")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
