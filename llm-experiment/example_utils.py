"""
ユーティリティモジュールの使用例

このスクリプトは、ExperimentLoggerとConfigLoaderの基本的な使い方を示します。
"""

import sys
import logging
import tempfile
import json
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.utils import ExperimentLogger, ConfigLoader

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_logger():
    """ExperimentLoggerの使用例"""
    logger.info("=" * 60)
    logger.info("ExperimentLogger の使用例")
    logger.info("=" * 60)

    # 一時ディレクトリで実行
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. ロガーの初期化
        logger.info("\n1. ExperimentLoggerの初期化")
        exp_logger = ExperimentLogger(log_dir=tmpdir)
        logger.info(f"✓ セッションID: {exp_logger.session_id}")

        # 2. リクエストログ
        logger.info("\n2. リクエストログの記録")
        exp_logger.log_request("gpt-4o", "contract_01.pdf")
        logger.info("✓ リクエストを記録しました")

        # 3. レスポンスログ
        logger.info("\n3. レスポンスログの記録")
        tokens = {"input_tokens": 10000, "output_tokens": 3000}
        exp_logger.log_response(
            model="gpt-4o",
            pdf_name="contract_01.pdf",
            response_time=2.5,
            tokens=tokens,
            success=True
        )
        logger.info("✓ レスポンスを記録しました")

        # 4. 評価ログ
        logger.info("\n4. 評価ログの記録")
        metrics = {
            "field_accuracy": 0.95,
            "f1_score": 0.92,
            "exact_match": False,
            "schema_valid": True,
            "statistics": {
                "total_fields": 50,
                "correct_fields": 47,
                "incorrect_fields": 3,
                "missing_fields": 0,
                "extra_fields": 0
            }
        }
        exp_logger.log_evaluation(
            model="gpt-4o",
            pdf_name="contract_01.pdf",
            metrics=metrics,
            cost=187.5
        )
        logger.info("✓ 評価を記録しました")

        # 5. 複数のログを追加
        logger.info("\n5. 複数のログを追加")
        for i in range(2, 4):
            pdf_name = f"contract_{i:02d}.pdf"
            exp_logger.log_request("gpt-4o", pdf_name)
            exp_logger.log_response(
                "gpt-4o", pdf_name, 2.3,
                {"input_tokens": 9000, "output_tokens": 2800},
                True
            )
            exp_logger.log_evaluation(
                "gpt-4o", pdf_name,
                {"field_accuracy": 0.93, "f1_score": 0.90, "exact_match": False, "schema_valid": True},
                175.0
            )

        logger.info(f"✓ 合計{len(exp_logger.evaluation_logs)}件のログを記録")

        # 6. 統計情報の取得
        logger.info("\n6. 統計情報の取得")
        stats = exp_logger.get_statistics()
        logger.info(f"  総リクエスト: {stats['total_requests']}")
        logger.info(f"  総レスポンス: {stats['total_responses']}")
        logger.info(f"  総評価: {stats['total_evaluations']}")
        logger.info(f"  成功率: {stats['success_rate']:.2%}")

        # 7. サマリーレポートの生成
        logger.info("\n7. サマリーレポートの生成")
        summary = exp_logger.generate_summary_report()
        logger.info(f"  セッションID: {summary['session_id']}")
        logger.info(f"  評価件数: {summary['total_evaluations']}")
        for model, data in summary['models'].items():
            logger.info(f"  {model}:")
            logger.info(f"    - 平均項目正答率: {data['avg_field_accuracy']:.2%}")
            logger.info(f"    - 平均F1スコア: {data['avg_f1_score']:.4f}")
            logger.info(f"    - 平均コスト: {data['avg_cost_per_pdf']:.2f}円")

        # 8. CSV保存
        logger.info("\n8. CSV保存")
        csv_path = exp_logger.save_to_csv(f"{tmpdir}/results.csv")
        logger.info(f"✓ CSVを保存しました: {csv_path}")

        # 9. サマリーレポート保存
        logger.info("\n9. サマリーレポート保存")
        report_path = exp_logger.save_summary_report(f"{tmpdir}/summary.json")
        logger.info(f"✓ サマリーを保存しました: {report_path}")

        # 10. サマリー表示
        logger.info("\n10. サマリー表示")
        exp_logger.print_summary()


def example_config_loader():
    """ConfigLoaderの使用例"""
    logger.info("\n" + "=" * 60)
    logger.info("ConfigLoader の使用例")
    logger.info("=" * 60)

    # 1. ConfigLoaderの初期化
    logger.info("\n1. ConfigLoaderの初期化")
    config_loader = ConfigLoader(config_dir="config")
    logger.info("✓ ConfigLoaderを初期化しました")

    # 2. 価格設定の読み込み
    logger.info("\n2. 価格設定の読み込み")
    try:
        pricing = config_loader.load_pricing()
        logger.info(f"✓ 価格設定を読み込みました: {len(pricing)}モデル")

        # 最初のモデルの情報を表示
        first_model = list(pricing.keys())[0]
        logger.info(f"  例: {first_model}")
        logger.info(f"    入力価格: ${pricing[first_model]['input_token_price_per_1m']}/1M tokens")
        logger.info(f"    出力価格: ${pricing[first_model]['output_token_price_per_1m']}/1M tokens")

    except Exception as e:
        logger.error(f"✗ 価格設定の読み込み失敗: {str(e)}")

    # 3. システムプロンプトの読み込み
    logger.info("\n3. システムプロンプトの読み込み")
    try:
        prompt = config_loader.load_system_prompt()
        logger.info(f"✓ システムプロンプトを読み込みました: {len(prompt)}文字")
        logger.info(f"  最初の100文字: {prompt[:100]}...")
    except Exception as e:
        logger.error(f"✗ プロンプトの読み込み失敗: {str(e)}")

    # 4. APIキーの読み込み（デモ用）
    logger.info("\n4. APIキーの読み込み")
    try:
        api_keys = config_loader.load_api_keys()
        logger.info(f"✓ APIキーを読み込みました: {list(api_keys.keys())}")
    except Exception as e:
        logger.warning(f"⚠ APIキーの読み込み失敗: {str(e)}")
        logger.info("  APIキー設定については、config/api_keys.example.json を参照してください")

    # 5. スキーマの読み込み
    logger.info("\n5. JSONスキーマの読み込み")
    try:
        schema = config_loader.load_schema()
        if schema:
            logger.info(f"✓ JSONスキーマを読み込みました")
        else:
            logger.warning("⚠ JSONスキーマが設定されていません")
    except Exception as e:
        logger.warning(f"⚠ スキーマの読み込み失敗: {str(e)}")

    # 6. 設定の検証
    logger.info("\n6. 設定の検証")
    is_valid = config_loader.validate_config()
    if is_valid:
        logger.info("✓ すべての設定が有効です")
    else:
        logger.warning("⚠ 一部の設定が無効です")

    # 7. 全設定の一括取得
    logger.info("\n7. 全設定の一括取得")
    all_configs = config_loader.get_all_configs()
    logger.info("✓ 全設定を取得しました:")
    for key in all_configs.keys():
        logger.info(f"  - {key}")


def example_integrated():
    """統合使用例"""
    logger.info("\n" + "=" * 60)
    logger.info("統合使用例: 実験フローのシミュレーション")
    logger.info("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        # 設定読み込み
        logger.info("\n1. 設定読み込み")
        config_loader = ConfigLoader("config")
        configs = config_loader.get_all_configs()
        logger.info(f"✓ 設定読み込み完了")

        # ロガー初期化
        logger.info("\n2. ロガー初期化")
        exp_logger = ExperimentLogger(tmpdir)
        logger.info(f"✓ セッションID: {exp_logger.session_id}")

        # 実験シミュレーション
        logger.info("\n3. 実験シミュレーション")
        models = ["gpt-4o", "claude-3-sonnet"]
        pdfs = ["contract_01", "contract_02"]

        for pdf_name in pdfs:
            for model in models:
                # リクエスト
                exp_logger.log_request(model, pdf_name)

                # レスポンス
                import random
                response_time = random.uniform(1.5, 3.0)
                tokens = {
                    "input_tokens": random.randint(8000, 12000),
                    "output_tokens": random.randint(2000, 4000)
                }
                exp_logger.log_response(model, pdf_name, response_time, tokens, True)

                # 評価
                metrics = {
                    "field_accuracy": random.uniform(0.85, 0.98),
                    "f1_score": random.uniform(0.80, 0.95),
                    "exact_match": random.choice([True, False]),
                    "schema_valid": True
                }
                cost = random.uniform(100, 250)
                exp_logger.log_evaluation(model, pdf_name, metrics, cost)

        logger.info(f"✓ {len(pdfs)} PDF × {len(models)} モデルの実験完了")

        # 結果表示
        logger.info("\n4. 結果の集計と表示")
        exp_logger.print_summary()

        # 保存
        logger.info("\n5. 結果の保存")
        csv_path = exp_logger.save_to_csv(f"{tmpdir}/results.csv")
        summary_path = exp_logger.save_summary_report(f"{tmpdir}/summary.json")
        logger.info(f"✓ CSV保存: {csv_path}")
        logger.info(f"✓ サマリー保存: {summary_path}")


def main():
    """メイン関数"""
    logger.info("ユーティリティモジュールの使用例を実行します\n")

    # ExperimentLoggerの使用例
    example_logger()

    # ConfigLoaderの使用例
    example_config_loader()

    # 統合使用例
    example_integrated()

    logger.info("\n" + "=" * 60)
    logger.info("使用例の実行が完了しました")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
