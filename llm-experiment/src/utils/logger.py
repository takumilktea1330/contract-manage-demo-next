"""
ログ管理モジュール

実験の実行ログ、APIリクエスト/レスポンス、評価結果を記録する。
"""

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd


logger = logging.getLogger(__name__)


class ExperimentLogger:
    """実験ログを管理するクラス"""

    def __init__(self, log_dir: str = "output/logs"):
        """
        ExperimentLoggerの初期化

        Args:
            log_dir: ログ出力ディレクトリ
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # ログデータを保持するリスト
        self.request_logs: List[Dict] = []
        self.response_logs: List[Dict] = []
        self.evaluation_logs: List[Dict] = []
        self.error_logs: List[Dict] = []

        # タイムスタンプ
        self.session_start = datetime.now()
        self.session_id = self.session_start.strftime("%Y%m%d_%H%M%S")

        # ロガーの設定
        self._setup_file_logger()

        logger.info(f"ExperimentLogger初期化完了: セッションID={self.session_id}")

    def _setup_file_logger(self):
        """ファイルロガーの設定"""
        log_file = self.log_dir / f"experiment_{self.session_id}.log"

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        # ルートロガーに追加
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        root_logger.setLevel(logging.INFO)

        logger.info(f"ログファイル作成: {log_file}")

    def log_request(
        self,
        model: str,
        pdf_name: str,
        timestamp: Optional[str] = None
    ) -> None:
        """
        APIリクエストを記録する

        Args:
            model: モデル名
            pdf_name: PDFファイル名
            timestamp: タイムスタンプ（指定がない場合は現在時刻）
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        request_log = {
            'timestamp': timestamp,
            'model': model,
            'pdf_name': pdf_name,
            'session_id': self.session_id
        }

        self.request_logs.append(request_log)
        logger.info(f"リクエスト記録: {model} - {pdf_name}")

    def log_response(
        self,
        model: str,
        pdf_name: str,
        response_time: float,
        tokens: Dict[str, int],
        success: bool = True,
        error_message: Optional[str] = None
    ) -> None:
        """
        APIレスポンスを記録する

        Args:
            model: モデル名
            pdf_name: PDFファイル名
            response_time: 応答時間（秒）
            tokens: トークン情報 {'input_tokens': int, 'output_tokens': int}
            success: 成功したか
            error_message: エラーメッセージ（失敗時）
        """
        response_log = {
            'timestamp': datetime.now().isoformat(),
            'model': model,
            'pdf_name': pdf_name,
            'response_time': response_time,
            'input_tokens': tokens.get('input_tokens', 0),
            'output_tokens': tokens.get('output_tokens', 0),
            'total_tokens': tokens.get('input_tokens', 0) + tokens.get('output_tokens', 0),
            'success': success,
            'error_message': error_message,
            'session_id': self.session_id
        }

        self.response_logs.append(response_log)

        if success:
            logger.info(
                f"レスポンス記録: {model} - {pdf_name} "
                f"({response_time:.2f}秒, {response_log['total_tokens']:,}トークン)"
            )
        else:
            logger.error(
                f"レスポンス失敗: {model} - {pdf_name} - {error_message}"
            )

    def log_evaluation(
        self,
        model: str,
        pdf_name: str,
        metrics: Dict[str, Any],
        cost: Optional[float] = None
    ) -> None:
        """
        評価結果を記録する

        Args:
            model: モデル名
            pdf_name: PDFファイル名
            metrics: 評価指標 {'field_accuracy': float, 'f1_score': float, ...}
            cost: コスト（円）
        """
        evaluation_log = {
            'timestamp': datetime.now().isoformat(),
            'model': model,
            'pdf_name': pdf_name,
            'field_accuracy': metrics.get('field_accuracy', 0.0),
            'f1_score': metrics.get('f1_score', 0.0),
            'exact_match': metrics.get('exact_match', False),
            'schema_valid': metrics.get('schema_valid', False),
            'cost_jpy': cost,
            'session_id': self.session_id
        }

        # 統計情報があれば追加
        if 'statistics' in metrics:
            stats = metrics['statistics']
            evaluation_log.update({
                'total_fields': stats.get('total_fields', 0),
                'correct_fields': stats.get('correct_fields', 0),
                'incorrect_fields': stats.get('incorrect_fields', 0),
                'missing_fields': stats.get('missing_fields', 0),
                'extra_fields': stats.get('extra_fields', 0)
            })

        self.evaluation_logs.append(evaluation_log)

        logger.info(
            f"評価記録: {model} - {pdf_name} "
            f"(正答率={evaluation_log['field_accuracy']:.2%}, "
            f"F1={evaluation_log['f1_score']:.4f})"
        )

    def log_error(
        self,
        model: str,
        pdf_name: str,
        error: Exception,
        error_type: str = "unknown"
    ) -> None:
        """
        エラーを記録する

        Args:
            model: モデル名
            pdf_name: PDFファイル名
            error: 例外オブジェクト
            error_type: エラータイプ
        """
        error_log = {
            'timestamp': datetime.now().isoformat(),
            'model': model,
            'pdf_name': pdf_name,
            'error_type': error_type,
            'error_message': str(error),
            'error_class': error.__class__.__name__,
            'session_id': self.session_id
        }

        self.error_logs.append(error_log)
        logger.error(
            f"エラー記録: {model} - {pdf_name} - {error_type}: {str(error)}"
        )

    def save_to_csv(self, output_path: Optional[str] = None) -> str:
        """
        ログをCSVファイルに保存する

        Args:
            output_path: 出力ファイルパス（指定がない場合は自動生成）

        Returns:
            保存したファイルパス
        """
        if output_path is None:
            output_path = self.log_dir.parent / "results" / f"metrics_{self.session_id}.csv"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 評価ログとレスポンスログをマージ
        merged_logs = []

        for eval_log in self.evaluation_logs:
            # 対応するレスポンスログを探す
            response_log = None
            for resp in self.response_logs:
                if (resp['model'] == eval_log['model'] and
                    resp['pdf_name'] == eval_log['pdf_name']):
                    response_log = resp
                    break

            merged = eval_log.copy()
            if response_log:
                merged.update({
                    'response_time': response_log.get('response_time', 0.0),
                    'input_tokens': response_log.get('input_tokens', 0),
                    'output_tokens': response_log.get('output_tokens', 0),
                    'total_tokens': response_log.get('total_tokens', 0)
                })

            merged_logs.append(merged)

        # CSVに書き込み
        if merged_logs:
            df = pd.DataFrame(merged_logs)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            logger.info(f"CSVファイル保存: {output_path} ({len(merged_logs)}行)")
        else:
            logger.warning("保存するログデータがありません")

        return str(output_path)

    def generate_summary_report(self) -> Dict:
        """
        サマリーレポートを生成する

        Returns:
            サマリーレポートの辞書
        """
        if not self.evaluation_logs:
            logger.warning("評価ログがありません")
            return {
                'session_id': self.session_id,
                'session_start': self.session_start.isoformat(),
                'total_evaluations': 0,
                'models': {}
            }

        # モデルごとに集計
        models_summary = {}
        model_names = set(log['model'] for log in self.evaluation_logs)

        for model in model_names:
            model_logs = [log for log in self.evaluation_logs if log['model'] == model]

            if not model_logs:
                continue

            # 平均値を計算
            avg_field_accuracy = sum(log['field_accuracy'] for log in model_logs) / len(model_logs)
            avg_f1_score = sum(log['f1_score'] for log in model_logs) / len(model_logs)
            exact_match_count = sum(1 for log in model_logs if log['exact_match'])
            exact_match_rate = exact_match_count / len(model_logs)
            schema_valid_count = sum(1 for log in model_logs if log['schema_valid'])
            schema_conformance_rate = schema_valid_count / len(model_logs)

            # コストを集計
            costs = [log['cost_jpy'] for log in model_logs if log['cost_jpy'] is not None]
            avg_cost = sum(costs) / len(costs) if costs else 0.0
            total_cost = sum(costs) if costs else 0.0

            # レスポンスタイムを集計
            response_times = []
            total_tokens = 0
            for log in model_logs:
                for resp in self.response_logs:
                    if (resp['model'] == model and
                        resp['pdf_name'] == log['pdf_name']):
                        response_times.append(resp['response_time'])
                        total_tokens += resp['total_tokens']
                        break

            avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0

            models_summary[model] = {
                'count': len(model_logs),
                'avg_field_accuracy': avg_field_accuracy,
                'avg_f1_score': avg_f1_score,
                'exact_match_rate': exact_match_rate,
                'schema_conformance_rate': schema_conformance_rate,
                'avg_cost_per_pdf': avg_cost,
                'total_cost': total_cost,
                'avg_response_time': avg_response_time,
                'total_tokens': total_tokens
            }

        summary = {
            'session_id': self.session_id,
            'session_start': self.session_start.isoformat(),
            'session_end': datetime.now().isoformat(),
            'total_evaluations': len(self.evaluation_logs),
            'total_errors': len(self.error_logs),
            'models': models_summary
        }

        logger.info(f"サマリーレポート生成完了: {len(models_summary)}モデル")
        return summary

    def save_summary_report(self, output_path: Optional[str] = None) -> str:
        """
        サマリーレポートをJSONファイルに保存する

        Args:
            output_path: 出力ファイルパス

        Returns:
            保存したファイルパス
        """
        if output_path is None:
            output_path = self.log_dir.parent / "results" / f"summary_{self.session_id}.json"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        summary = self.generate_summary_report()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        logger.info(f"サマリーレポート保存: {output_path}")
        return str(output_path)

    def get_statistics(self) -> Dict:
        """
        実行統計を取得する

        Returns:
            統計情報の辞書
        """
        stats = {
            'total_requests': len(self.request_logs),
            'total_responses': len(self.response_logs),
            'total_evaluations': len(self.evaluation_logs),
            'total_errors': len(self.error_logs),
            'success_rate': 0.0
        }

        if self.response_logs:
            success_count = sum(1 for log in self.response_logs if log['success'])
            stats['success_rate'] = success_count / len(self.response_logs)

        return stats

    def print_summary(self) -> None:
        """サマリーレポートをコンソールに出力する"""
        summary = self.generate_summary_report()

        print("\n" + "=" * 80)
        print("実験サマリーレポート")
        print("=" * 80)
        print(f"セッションID: {summary['session_id']}")
        print(f"開始時刻: {summary['session_start']}")
        print(f"終了時刻: {summary['session_end']}")
        print(f"評価件数: {summary['total_evaluations']}")
        print(f"エラー件数: {summary['total_errors']}")
        print()

        for model, data in summary['models'].items():
            print(f"モデル: {model}")
            print(f"  処理件数: {data['count']}")
            print(f"  平均項目正答率: {data['avg_field_accuracy']:.2%}")
            print(f"  平均F1スコア: {data['avg_f1_score']:.4f}")
            print(f"  完全一致率: {data['exact_match_rate']:.2%}")
            print(f"  スキーマ準拠率: {data['schema_conformance_rate']:.2%}")
            print(f"  平均コスト/PDF: {data['avg_cost_per_pdf']:.2f}円")
            print(f"  合計コスト: {data['total_cost']:.2f}円")
            print(f"  平均応答時間: {data['avg_response_time']:.2f}秒")
            print(f"  合計トークン: {data['total_tokens']:,}")
            print()

        print("=" * 80)
