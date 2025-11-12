"""
ログ管理モジュールのテスト
"""

import pytest
import tempfile
from pathlib import Path
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import ExperimentLogger


class TestExperimentLogger:
    """ExperimentLoggerクラスのテスト"""

    @pytest.fixture
    def logger(self):
        """一時ディレクトリを使用したロガーを返す"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = ExperimentLogger(log_dir=tmpdir)
            yield logger

    def test_logger_initialization(self, logger):
        """ロガーの初期化テスト"""
        assert logger is not None
        assert logger.session_id is not None
        assert logger.log_dir.exists()

    def test_log_request(self, logger):
        """リクエストログのテスト"""
        logger.log_request("test-model", "test.pdf")
        assert len(logger.request_logs) == 1
        assert logger.request_logs[0]['model'] == "test-model"
        assert logger.request_logs[0]['pdf_name'] == "test.pdf"

    def test_log_response_success(self, logger):
        """成功レスポンスログのテスト"""
        tokens = {"input_tokens": 1000, "output_tokens": 500}
        logger.log_response("test-model", "test.pdf", 2.5, tokens, success=True)

        assert len(logger.response_logs) == 1
        assert logger.response_logs[0]['success'] is True
        assert logger.response_logs[0]['response_time'] == 2.5
        assert logger.response_logs[0]['input_tokens'] == 1000
        assert logger.response_logs[0]['output_tokens'] == 500
        assert logger.response_logs[0]['total_tokens'] == 1500

    def test_log_response_failure(self, logger):
        """失敗レスポンスログのテスト"""
        tokens = {"input_tokens": 0, "output_tokens": 0}
        logger.log_response(
            "test-model", "test.pdf", 0.0, tokens,
            success=False, error_message="API Error"
        )

        assert len(logger.response_logs) == 1
        assert logger.response_logs[0]['success'] is False
        assert logger.response_logs[0]['error_message'] == "API Error"

    def test_log_evaluation(self, logger):
        """評価ログのテスト"""
        metrics = {
            "field_accuracy": 0.95,
            "f1_score": 0.92,
            "exact_match": False,
            "schema_valid": True
        }
        logger.log_evaluation("test-model", "test.pdf", metrics, cost=150.0)

        assert len(logger.evaluation_logs) == 1
        assert logger.evaluation_logs[0]['field_accuracy'] == 0.95
        assert logger.evaluation_logs[0]['f1_score'] == 0.92
        assert logger.evaluation_logs[0]['cost_jpy'] == 150.0

    def test_log_error(self, logger):
        """エラーログのテスト"""
        error = ValueError("Test error")
        logger.log_error("test-model", "test.pdf", error, "test_error")

        assert len(logger.error_logs) == 1
        assert logger.error_logs[0]['error_type'] == "test_error"
        assert logger.error_logs[0]['error_class'] == "ValueError"
        assert "Test error" in logger.error_logs[0]['error_message']

    def test_get_statistics(self, logger):
        """統計取得のテスト"""
        logger.log_request("model1", "pdf1")
        logger.log_response("model1", "pdf1", 1.0, {"input_tokens": 100, "output_tokens": 50}, True)

        stats = logger.get_statistics()
        assert stats['total_requests'] == 1
        assert stats['total_responses'] == 1
        assert stats['success_rate'] == 1.0

    def test_generate_summary_report(self, logger):
        """サマリーレポート生成のテスト"""
        # データ追加
        metrics = {"field_accuracy": 0.9, "f1_score": 0.85, "exact_match": False, "schema_valid": True}
        logger.log_evaluation("model1", "pdf1", metrics, 100.0)
        logger.log_response("model1", "pdf1", 2.0, {"input_tokens": 1000, "output_tokens": 500}, True)

        summary = logger.generate_summary_report()

        assert 'session_id' in summary
        assert 'models' in summary
        assert 'model1' in summary['models']
        assert summary['models']['model1']['count'] == 1

    def test_save_to_csv(self):
        """CSV保存のテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = ExperimentLogger(log_dir=tmpdir)

            # データ追加
            metrics = {"field_accuracy": 0.9, "f1_score": 0.85, "exact_match": False, "schema_valid": True}
            logger.log_evaluation("model1", "pdf1", metrics, 100.0)
            logger.log_response("model1", "pdf1", 2.0, {"input_tokens": 1000, "output_tokens": 500}, True)

            # CSV保存
            csv_path = logger.save_to_csv()

            assert Path(csv_path).exists()
            assert Path(csv_path).suffix == '.csv'

    def test_save_summary_report(self):
        """サマリーレポート保存のテスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = ExperimentLogger(log_dir=tmpdir)

            # データ追加
            metrics = {"field_accuracy": 0.9, "f1_score": 0.85, "exact_match": False, "schema_valid": True}
            logger.log_evaluation("model1", "pdf1", metrics, 100.0)

            # レポート保存
            report_path = logger.save_summary_report()

            assert Path(report_path).exists()
            assert Path(report_path).suffix == '.json'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
