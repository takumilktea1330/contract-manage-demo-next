"""
メイン実行スクリプト

PDF データ抽出 LLM 比較実験のメイン処理を実行する。
"""

import argparse
import json
import logging
import sys
import time
from glob import glob
from pathlib import Path
from typing import Dict, List, Optional

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processors import PDFProcessor, ImageConverter
from src.evaluators import SchemaValidator, AccuracyCalculator, CostCalculator
from src.utils import ExperimentLogger, ConfigLoader
from src.visualizers import ResultVisualizer


# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExperimentRunner:
    """実験を実行するクラス"""

    def __init__(
        self,
        config_dir: str = "config",
        data_dir: str = "data",
        output_dir: str = "output"
    ):
        """
        ExperimentRunnerの初期化

        Args:
            config_dir: 設定ファイルディレクトリ
            data_dir: データディレクトリ
            output_dir: 出力ディレクトリ
        """
        self.config_dir = Path(config_dir)
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)

        # 各種マネージャーの初期化
        self.config_loader = ConfigLoader(config_dir)
        self.logger = ExperimentLogger(output_dir / "logs")

        # 設定の読み込み
        self.configs = self._load_configs()

        # プロセッサーの初期化
        self.pdf_processor = PDFProcessor()
        self.image_converter = ImageConverter(dpi=200, max_size_mb=10.0)

        # 評価ツールの初期化
        self.cost_calculator = CostCalculator(self.configs.get('pricing', {}))

        # スキーマバリデータ（スキーマがあれば）
        self.schema_validator = None
        if self.configs.get('schema'):
            self.schema_validator = SchemaValidator(self.configs['schema'])

        logger.info("ExperimentRunner初期化完了")

    def _load_configs(self) -> Dict:
        """設定を読み込む"""
        logger.info("設定を読み込み中...")

        # 設定の検証
        if not self.config_loader.validate_config():
            logger.warning("一部の設定が無効です。続行しますか？")

        configs = self.config_loader.get_all_configs()
        logger.info(f"設定読み込み完了: {list(configs.keys())}")

        return configs

    def get_pdf_list(self, pattern: Optional[str] = None) -> List[Path]:
        """
        処理するPDFのリストを取得する

        Args:
            pattern: PDFファイルのパターン（例: "contract_*.pdf"）

        Returns:
            PDFファイルのパスリスト
        """
        input_dir = self.data_dir / "input"

        if pattern:
            pdf_files = list(input_dir.glob(pattern))
        else:
            pdf_files = list(input_dir.glob("*.pdf"))

        pdf_files.sort()
        logger.info(f"処理対象PDF: {len(pdf_files)}件")

        return pdf_files

    def load_golden_data(self, pdf_name: str) -> Optional[Dict]:
        """
        正解データ（Golden Standard）を読み込む

        Args:
            pdf_name: PDFファイル名（拡張子なし）

        Returns:
            正解データの辞書（存在しない場合はNone）
        """
        golden_path = self.data_dir / "golden" / f"{pdf_name}.json"

        if not golden_path.exists():
            logger.warning(f"正解データが見つかりません: {golden_path}")
            return None

        try:
            with open(golden_path, 'r', encoding='utf-8') as f:
                golden_data = json.load(f)

            logger.info(f"正解データ読み込み: {golden_path}")
            return golden_data

        except Exception as e:
            logger.error(f"正解データの読み込み失敗: {golden_path}, {str(e)}")
            return None

    def extract_data_mock(
        self,
        pdf_path: Path,
        model: str,
        system_prompt: str
    ) -> Dict:
        """
        データ抽出のモック実装（API連携モジュールが実装されるまでの仮実装）

        Args:
            pdf_path: PDFファイルパス
            model: モデル名
            system_prompt: システムプロンプト

        Returns:
            抽出結果とメタデータの辞書
        """
        logger.info(f"[MOCK] データ抽出: {model} - {pdf_path.name}")

        # PDFを画像に変換（実際の処理）
        try:
            images = self.image_converter.pdf_to_images(str(pdf_path), dpi=150)
            logger.info(f"PDF→画像変換完了: {len(images)}ページ")
        except Exception as e:
            logger.error(f"PDF変換エラー: {str(e)}")
            raise

        # モックデータを返す
        # TODO: 実際のAPI連携モジュールに置き換える
        mock_extracted_data = {
            "contract_type": "普通賃貸借契約",
            "contract_date": "2024-01-01",
            "rent": 100000,
            "deposit": 200000
        }

        # トークン数もモック
        mock_tokens = {
            "input_tokens": len(images) * 1000,  # 1ページあたり1000トークンと仮定
            "output_tokens": 500
        }

        return {
            "extracted_data": mock_extracted_data,
            "tokens": mock_tokens,
            "success": True,
            "error_message": None
        }

    def run_extraction(
        self,
        pdf_path: Path,
        model: str
    ) -> Optional[Dict]:
        """
        1つのPDFに対してデータ抽出を実行する

        Args:
            pdf_path: PDFファイルパス
            model: モデル名

        Returns:
            抽出結果の辞書（失敗時はNone）
        """
        pdf_name = pdf_path.stem

        try:
            # PDFの検証
            is_valid, error_msg = self.pdf_processor.validate_pdf(str(pdf_path))
            if not is_valid:
                logger.error(f"PDF検証失敗: {pdf_path.name} - {error_msg}")
                return None

            # リクエストログ
            self.logger.log_request(model, pdf_name)

            # データ抽出
            start_time = time.time()

            # TODO: 実際のAPI連携に置き換える
            result = self.extract_data_mock(
                pdf_path,
                model,
                self.configs.get('system_prompt', '')
            )

            response_time = time.time() - start_time

            # レスポンスログ
            self.logger.log_response(
                model=model,
                pdf_name=pdf_name,
                response_time=response_time,
                tokens=result['tokens'],
                success=result['success'],
                error_message=result.get('error_message')
            )

            if not result['success']:
                return None

            # 抽出結果を保存
            output_path = self.output_dir / "extracted" / f"{model}_{pdf_name}.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result['extracted_data'], f, ensure_ascii=False, indent=2)

            logger.info(f"抽出結果保存: {output_path}")

            return result

        except Exception as e:
            logger.error(f"抽出処理エラー: {model} - {pdf_path.name} - {str(e)}")
            self.logger.log_error(model, pdf_name, e, "extraction_error")
            return None

    def run_evaluation(
        self,
        pdf_name: str,
        model: str,
        extracted_data: Dict,
        tokens: Dict[str, int]
    ) -> Optional[Dict]:
        """
        抽出結果を評価する

        Args:
            pdf_name: PDFファイル名
            model: モデル名
            extracted_data: 抽出データ
            tokens: トークン情報

        Returns:
            評価結果の辞書（失敗時はNone）
        """
        try:
            # 正解データの読み込み
            golden_data = self.load_golden_data(pdf_name)

            if golden_data is None:
                logger.warning(f"正解データがないため評価をスキップ: {pdf_name}")
                return None

            # スキーマ検証
            schema_valid = True
            schema_errors = []

            if self.schema_validator:
                schema_valid, schema_errors = self.schema_validator.validate(extracted_data)

            # 精度計算
            accuracy_calc = AccuracyCalculator(golden_data, extracted_data)
            metrics = accuracy_calc.get_metrics()
            metrics['schema_valid'] = schema_valid

            # コスト計算
            cost_jpy = self.cost_calculator.calculate_cost(
                model=model,
                input_tokens=tokens['input_tokens'],
                output_tokens=tokens['output_tokens'],
                currency='JPY'
            )

            # 評価ログ
            self.logger.log_evaluation(
                model=model,
                pdf_name=pdf_name,
                metrics=metrics,
                cost=cost_jpy
            )

            return {
                'metrics': metrics,
                'cost_jpy': cost_jpy,
                'schema_valid': schema_valid,
                'schema_errors': schema_errors
            }

        except Exception as e:
            logger.error(f"評価エラー: {model} - {pdf_name} - {str(e)}")
            self.logger.log_error(model, pdf_name, e, "evaluation_error")
            return None

    def run_experiment(
        self,
        models: List[str],
        pdf_pattern: Optional[str] = None,
        skip_evaluation: bool = False,
        skip_visualization: bool = False
    ) -> None:
        """
        実験を実行する

        Args:
            models: 実行するモデルのリスト
            pdf_pattern: PDFファイルパターン
            skip_evaluation: 評価をスキップするか
            skip_visualization: 可視化をスキップするか
        """
        logger.info("=" * 80)
        logger.info("実験開始")
        logger.info("=" * 80)

        # PDFリストの取得
        pdf_files = self.get_pdf_list(pdf_pattern)

        if not pdf_files:
            logger.error("処理対象のPDFが見つかりません")
            return

        logger.info(f"処理対象: {len(pdf_files)} PDF × {len(models)} モデル")

        # 実験実行
        total_tasks = len(pdf_files) * len(models)
        completed_tasks = 0

        for pdf_path in pdf_files:
            pdf_name = pdf_path.stem
            logger.info(f"\n処理中: {pdf_path.name}")

            for model in models:
                completed_tasks += 1
                logger.info(
                    f"[{completed_tasks}/{total_tasks}] {model} - {pdf_path.name}"
                )

                try:
                    # データ抽出
                    result = self.run_extraction(pdf_path, model)

                    if result is None:
                        logger.warning(f"抽出失敗: {model} - {pdf_path.name}")
                        continue

                    # 評価
                    if not skip_evaluation:
                        eval_result = self.run_evaluation(
                            pdf_name=pdf_name,
                            model=model,
                            extracted_data=result['extracted_data'],
                            tokens=result['tokens']
                        )

                        if eval_result is None:
                            logger.warning(f"評価失敗: {model} - {pdf_path.name}")

                except Exception as e:
                    logger.error(f"タスク失敗: {model} - {pdf_path.name} - {str(e)}")
                    self.logger.log_error(model, pdf_name, e, "task_error")
                    continue

        logger.info("\n" + "=" * 80)
        logger.info("実験完了")
        logger.info("=" * 80)

        # 結果の保存
        self._save_results(generate_visualizations=not skip_visualization)

    def _save_results(self, generate_visualizations: bool = True) -> None:
        """
        結果を保存する

        Args:
            generate_visualizations: 可視化を生成するか
        """
        logger.info("\n結果を保存中...")

        # CSVに保存
        csv_path = self.logger.save_to_csv()
        logger.info(f"✓ CSV保存: {csv_path}")

        # サマリーレポート保存
        summary_path = self.logger.save_summary_report()
        logger.info(f"✓ サマリー保存: {summary_path}")

        # 可視化の生成
        if generate_visualizations and self.logger.evaluation_logs:
            try:
                logger.info("\n可視化を生成中...")
                visualizer = ResultVisualizer(self.output_dir / "visualizations")
                generated_files = visualizer.generate_all_visualizations(
                    summary_path=summary_path,
                    csv_path=csv_path
                )
                logger.info(f"✓ 可視化生成完了: {len(generated_files)}ファイル")
                for file_path in generated_files:
                    logger.info(f"  - {Path(file_path).name}")
            except Exception as e:
                logger.error(f"✗ 可視化生成エラー: {str(e)}")

        # コンソールに出力
        self.logger.print_summary()


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="PDF データ抽出 LLM 比較実験"
    )

    parser.add_argument(
        "--models",
        nargs="+",
        default=["mock-model"],
        help="実行するモデル（例: gpt-4o claude-3-sonnet gemini-2.5-pro）"
    )

    parser.add_argument(
        "--pdf",
        help="特定のPDFのみ実行（パターン指定可。例: contract_*.pdf）"
    )

    parser.add_argument(
        "--skip-evaluation",
        action="store_true",
        help="評価をスキップ"
    )

    parser.add_argument(
        "--skip-visualization",
        action="store_true",
        help="可視化をスキップ"
    )

    parser.add_argument(
        "--config-dir",
        default="config",
        help="設定ファイルディレクトリ"
    )

    parser.add_argument(
        "--data-dir",
        default="data",
        help="データディレクトリ"
    )

    parser.add_argument(
        "--output-dir",
        default="output",
        help="出力ディレクトリ"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="API呼び出しなしでテスト実行"
    )

    args = parser.parse_args()

    try:
        # 実験ランナーの初期化
        runner = ExperimentRunner(
            config_dir=args.config_dir,
            data_dir=args.data_dir,
            output_dir=args.output_dir
        )

        if args.dry_run:
            logger.info("ドライランモード: 設定を確認して終了します")
            runner.config_loader.validate_config()
            pdf_files = runner.get_pdf_list(args.pdf)
            logger.info(f"処理対象PDF: {len(pdf_files)}件")
            logger.info(f"実行モデル: {args.models}")
            return

        # 実験実行
        runner.run_experiment(
            models=args.models,
            pdf_pattern=args.pdf,
            skip_evaluation=args.skip_evaluation,
            skip_visualization=args.skip_visualization
        )

        logger.info("\n✓ 実験が正常に完了しました")

    except KeyboardInterrupt:
        logger.warning("\n実験が中断されました")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n✗ 実験が失敗しました: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
