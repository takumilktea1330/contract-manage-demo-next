"""
可視化モジュールの使用例

このスクリプトは、ResultVisualizerの基本的な使い方を示します。
"""

import sys
import json
import logging
import tempfile
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.visualizers import ResultVisualizer

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_sample_summary():
    """サンプルのサマリーデータを作成"""
    return {
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
            },
            "claude-3-sonnet": {
                "count": 10,
                "avg_field_accuracy": 0.91,
                "avg_f1_score": 0.88,
                "exact_match_rate": 0.15,
                "schema_conformance_rate": 0.92,
                "avg_cost_per_pdf": 220.3,
                "total_cost": 2203.0,
                "avg_response_time": 2.15,
                "total_tokens": 145000
            },
            "gemini-2.5-flash": {
                "count": 10,
                "avg_field_accuracy": 0.88,
                "avg_f1_score": 0.85,
                "exact_match_rate": 0.08,
                "schema_conformance_rate": 0.90,
                "avg_cost_per_pdf": 45.2,
                "total_cost": 452.0,
                "avg_response_time": 1.85,
                "total_tokens": 125000
            }
        }
    }


def example_visualizer():
    """ResultVisualizerの使用例"""
    logger.info("=" * 60)
    logger.info("ResultVisualizer の使用例")
    logger.info("=" * 60)

    # 一時ディレクトリで実行
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. ResultVisualizerの初期化
        logger.info("\n1. ResultVisualizerの初期化")
        visualizer = ResultVisualizer(output_dir=f"{tmpdir}/visualizations")
        logger.info(f"✓ 出力ディレクトリ: {visualizer.output_dir}")

        # 2. サンプルデータの作成
        logger.info("\n2. サンプルデータの作成")
        summary = create_sample_summary()

        # サマリーを一時ファイルに保存
        summary_path = f"{tmpdir}/summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        logger.info(f"✓ サマリーファイル作成: {summary_path}")

        # 3. 精度比較グラフ
        logger.info("\n3. 精度比較グラフの作成")
        accuracy_path = visualizer.plot_accuracy_comparison(summary)
        logger.info(f"✓ 精度比較グラフ保存: {accuracy_path}")

        # 4. コスト vs 精度グラフ
        logger.info("\n4. コスト vs 精度グラフの作成")
        cost_vs_acc_path = visualizer.plot_cost_vs_accuracy(summary)
        logger.info(f"✓ コスト vs 精度グラフ保存: {cost_vs_acc_path}")

        # 5. レスポンスタイム比較グラフ
        logger.info("\n5. レスポンスタイム比較グラフの作成")
        response_time_path = visualizer.plot_response_time_comparison(summary)
        logger.info(f"✓ レスポンスタイム比較グラフ保存: {response_time_path}")

        # 6. レーダーチャート
        logger.info("\n6. レーダーチャートの作成")
        radar_path = visualizer.plot_radar_chart(summary)
        logger.info(f"✓ レーダーチャート保存: {radar_path}")

        # 7. コスト内訳グラフ
        logger.info("\n7. コスト内訳グラフの作成")
        cost_breakdown_path = visualizer.plot_cost_breakdown(summary)
        logger.info(f"✓ コスト内訳グラフ保存: {cost_breakdown_path}")

        # 8. トークン使用量グラフ
        logger.info("\n8. トークン使用量グラフの作成")
        token_usage_path = visualizer.plot_token_usage(summary)
        logger.info(f"✓ トークン使用量グラフ保存: {token_usage_path}")

        # 9. すべての可視化を一度に生成
        logger.info("\n9. すべての可視化を一度に生成")
        all_files = visualizer.generate_all_visualizations(summary_path)
        logger.info(f"✓ 生成されたファイル: {len(all_files)}個")
        for file_path in all_files:
            logger.info(f"  - {Path(file_path).name}")


def example_with_real_data():
    """実際のデータでの可視化例"""
    logger.info("\n" + "=" * 60)
    logger.info("実際のデータでの可視化例")
    logger.info("=" * 60)

    # 実際のサマリーファイルがあるか確認
    summary_path = Path("output/results").glob("summary_*.json")
    summary_files = list(summary_path)

    if not summary_files:
        logger.warning("\n実際のサマリーファイルが見つかりません")
        logger.info("まずは実験を実行してください:")
        logger.info("  python src/main.py")
        return

    # 最新のサマリーファイルを使用
    latest_summary = max(summary_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"\n使用するサマリーファイル: {latest_summary}")

    # 可視化を生成
    visualizer = ResultVisualizer(output_dir="output/visualizations")
    generated_files = visualizer.generate_all_visualizations(str(latest_summary))

    logger.info(f"\n✓ 可視化完了: {len(generated_files)}ファイル")
    logger.info("生成されたファイル:")
    for file_path in generated_files:
        logger.info(f"  - {file_path}")


def main():
    """メイン関数"""
    logger.info("可視化モジュールの使用例を実行します\n")

    # ResultVisualizerの使用例
    example_visualizer()

    # 実際のデータでの可視化例
    example_with_real_data()

    logger.info("\n" + "=" * 60)
    logger.info("使用例の実行が完了しました")
    logger.info("=" * 60)
    logger.info("\n実際のデータで可視化するには:")
    logger.info("1. 実験を実行: python src/main.py")
    logger.info("2. 可視化を生成: python example_visualizer.py")


if __name__ == '__main__':
    main()
