"""
結果可視化モジュールのテスト
"""

import pytest
import json
import tempfile
from pathlib import Path
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.visualizers import ResultVisualizer


class TestResultVisualizer:
    """ResultVisualizerクラスのテスト"""

    @pytest.fixture
    def visualizer(self):
        """一時ディレクトリを使用したvisualizerを返す"""
        with tempfile.TemporaryDirectory() as tmpdir:
            visualizer = ResultVisualizer(output_dir=tmpdir)
            yield visualizer

    @pytest.fixture
    def sample_summary(self):
        """サンプルのサマリーデータを返す"""
        return {
            "session_id": "test_session",
            "session_start": "2024-01-01T00:00:00",
            "session_end": "2024-01-01T01:00:00",
            "total_evaluations": 6,
            "total_errors": 0,
            "models": {
                "model1": {
                    "count": 3,
                    "avg_field_accuracy": 0.90,
                    "avg_f1_score": 0.85,
                    "exact_match_rate": 0.10,
                    "schema_conformance_rate": 0.95,
                    "avg_cost_per_pdf": 100.0,
                    "total_cost": 300.0,
                    "avg_response_time": 2.0,
                    "total_tokens": 10000
                },
                "model2": {
                    "count": 3,
                    "avg_field_accuracy": 0.85,
                    "avg_f1_score": 0.80,
                    "exact_match_rate": 0.05,
                    "schema_conformance_rate": 0.90,
                    "avg_cost_per_pdf": 50.0,
                    "total_cost": 150.0,
                    "avg_response_time": 1.5,
                    "total_tokens": 8000
                }
            }
        }

    def test_visualizer_initialization(self, visualizer):
        """初期化テスト"""
        assert visualizer is not None
        assert visualizer.output_dir.exists()

    def test_load_summary(self, visualizer, sample_summary):
        """サマリー読み込みテスト"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_summary, f)
            summary_path = f.name

        try:
            loaded_summary = visualizer.load_summary(summary_path)
            assert loaded_summary == sample_summary
        finally:
            Path(summary_path).unlink()

    def test_plot_accuracy_comparison(self, visualizer, sample_summary):
        """精度比較グラフ生成テスト"""
        output_path = visualizer.plot_accuracy_comparison(sample_summary)
        assert Path(output_path).exists()
        assert Path(output_path).suffix == '.png'

    def test_plot_cost_vs_accuracy(self, visualizer, sample_summary):
        """コスト vs 精度グラフ生成テスト"""
        output_path = visualizer.plot_cost_vs_accuracy(sample_summary)
        assert Path(output_path).exists()
        assert Path(output_path).suffix == '.png'

    def test_plot_response_time_comparison(self, visualizer, sample_summary):
        """レスポンスタイム比較グラフ生成テスト"""
        output_path = visualizer.plot_response_time_comparison(sample_summary)
        assert Path(output_path).exists()
        assert Path(output_path).suffix == '.png'

    def test_plot_radar_chart(self, visualizer, sample_summary):
        """レーダーチャート生成テスト"""
        output_path = visualizer.plot_radar_chart(sample_summary)
        assert Path(output_path).exists()
        assert Path(output_path).suffix == '.png'

    def test_plot_cost_breakdown(self, visualizer, sample_summary):
        """コスト内訳グラフ生成テスト"""
        output_path = visualizer.plot_cost_breakdown(sample_summary)
        assert Path(output_path).exists()
        assert Path(output_path).suffix == '.png'

    def test_plot_token_usage(self, visualizer, sample_summary):
        """トークン使用量グラフ生成テスト"""
        output_path = visualizer.plot_token_usage(sample_summary)
        assert Path(output_path).exists()
        assert Path(output_path).suffix == '.png'

    def test_generate_all_visualizations(self, visualizer, sample_summary):
        """すべての可視化生成テスト"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_summary, f)
            summary_path = f.name

        try:
            generated_files = visualizer.generate_all_visualizations(summary_path)
            assert len(generated_files) > 0
            for file_path in generated_files:
                assert Path(file_path).exists()
        finally:
            Path(summary_path).unlink()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
