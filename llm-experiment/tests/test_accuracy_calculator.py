"""
精度計算モジュールのテスト
"""

import pytest
import json
import tempfile
from pathlib import Path
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluators import AccuracyCalculator


class TestAccuracyCalculator:
    """AccuracyCalculatorクラスのテスト"""

    @pytest.fixture
    def golden_data(self):
        """正解データを返す"""
        return {
            "name": "田中太郎",
            "age": 30,
            "address": {
                "city": "東京都",
                "zip": "100-0001"
            },
            "hobbies": ["読書", "旅行"]
        }

    @pytest.fixture
    def extracted_data_perfect(self, golden_data):
        """完全一致する抽出データを返す"""
        return golden_data.copy()

    @pytest.fixture
    def extracted_data_partial(self):
        """部分的に一致する抽出データを返す"""
        return {
            "name": "田中太郎",
            "age": 31,  # 誤り
            "address": {
                "city": "東京都",
                "zip": "100-0002"  # 誤り
            },
            "hobbies": ["読書", "旅行"]
        }

    def test_calculator_initialization_with_dict(self, golden_data, extracted_data_perfect):
        """辞書での初期化テスト"""
        calculator = AccuracyCalculator(golden_data, extracted_data_perfect)
        assert calculator.golden_data == golden_data
        assert calculator.extracted_data == extracted_data_perfect

    def test_calculator_initialization_with_json_string(self, golden_data):
        """JSON文字列での初期化テスト"""
        golden_json = json.dumps(golden_data)
        extracted_json = json.dumps(golden_data)
        calculator = AccuracyCalculator(golden_json, extracted_json)
        assert calculator.golden_data == golden_data

    def test_calculate_field_accuracy_perfect(self, golden_data, extracted_data_perfect):
        """完全一致時の項目正答率テスト"""
        calculator = AccuracyCalculator(golden_data, extracted_data_perfect)
        accuracy = calculator.calculate_field_accuracy()
        assert accuracy == 1.0

    def test_calculate_field_accuracy_partial(self, golden_data, extracted_data_partial):
        """部分一致時の項目正答率テスト"""
        calculator = AccuracyCalculator(golden_data, extracted_data_partial)
        accuracy = calculator.calculate_field_accuracy()
        # name, address.city, hobbies が正しい (3/5)
        # age, address.zip が誤り
        assert 0.0 < accuracy < 1.0

    def test_calculate_f1_score_perfect(self, golden_data, extracted_data_perfect):
        """完全一致時のF1スコアテスト"""
        calculator = AccuracyCalculator(golden_data, extracted_data_perfect)
        f1_score = calculator.calculate_f1_score()
        assert f1_score == 1.0

    def test_calculate_f1_score_partial(self, golden_data, extracted_data_partial):
        """部分一致時のF1スコアテスト"""
        calculator = AccuracyCalculator(golden_data, extracted_data_partial)
        f1_score = calculator.calculate_f1_score()
        assert 0.0 < f1_score < 1.0

    def test_calculate_exact_match_perfect(self, golden_data, extracted_data_perfect):
        """完全一致時の完全一致判定テスト"""
        calculator = AccuracyCalculator(golden_data, extracted_data_perfect)
        exact_match = calculator.calculate_exact_match()
        assert exact_match is True

    def test_calculate_exact_match_partial(self, golden_data, extracted_data_partial):
        """部分一致時の完全一致判定テスト"""
        calculator = AccuracyCalculator(golden_data, extracted_data_partial)
        exact_match = calculator.calculate_exact_match()
        assert exact_match is False

    def test_compare_nested_dict(self, golden_data, extracted_data_partial):
        """ネストされた辞書の比較テスト"""
        calculator = AccuracyCalculator(golden_data, extracted_data_partial)
        result = calculator.compare_nested_dict(golden_data, extracted_data_partial)

        assert 'total_fields' in result
        assert 'correct_fields' in result
        assert 'incorrect_fields' in result
        assert 'missing_fields' in result
        assert 'extra_fields' in result
        assert 'field_details' in result

        assert result['total_fields'] > 0
        assert result['correct_fields'] > 0
        assert result['incorrect_fields'] > 0

    def test_get_detailed_diff(self, golden_data, extracted_data_partial):
        """詳細な差分取得テスト"""
        calculator = AccuracyCalculator(golden_data, extracted_data_partial)
        diff = calculator.get_detailed_diff()

        assert 'summary' in diff
        assert 'correct' in diff
        assert 'incorrect' in diff
        assert 'missing' in diff
        assert 'extra' in diff

        assert len(diff['correct']) > 0
        assert len(diff['incorrect']) > 0

    def test_get_metrics(self, golden_data, extracted_data_partial):
        """全評価指標取得テスト"""
        calculator = AccuracyCalculator(golden_data, extracted_data_partial)
        metrics = calculator.get_metrics()

        assert 'field_accuracy' in metrics
        assert 'f1_score' in metrics
        assert 'exact_match' in metrics
        assert 'statistics' in metrics
        assert 'timestamp' in metrics

        assert 0.0 <= metrics['field_accuracy'] <= 1.0
        assert 0.0 <= metrics['f1_score'] <= 1.0
        assert isinstance(metrics['exact_match'], bool)

    def test_missing_field(self, golden_data):
        """フィールド欠落時のテスト"""
        extracted = {
            "name": "田中太郎",
            "age": 30
            # address と hobbies が欠落
        }
        calculator = AccuracyCalculator(golden_data, extracted)
        result = calculator.compare_nested_dict(golden_data, extracted)

        assert result['missing_fields'] > 0

    def test_extra_field(self, golden_data):
        """余分なフィールドがある場合のテスト"""
        extracted = golden_data.copy()
        extracted['extra_field'] = "余分なデータ"

        calculator = AccuracyCalculator(golden_data, extracted)
        result = calculator.compare_nested_dict(golden_data, extracted)

        assert result['extra_fields'] > 0

    def test_list_comparison(self):
        """リスト比較のテスト"""
        golden = {"items": [1, 2, 3]}
        extracted_same = {"items": [1, 2, 3]}
        extracted_different = {"items": [1, 2, 4]}

        calc_same = AccuracyCalculator(golden, extracted_same)
        assert calc_same.calculate_exact_match() is True

        calc_different = AccuracyCalculator(golden, extracted_different)
        assert calc_different.calculate_exact_match() is False

    def test_numeric_tolerance(self):
        """数値の許容誤差テスト"""
        golden = {"value": 100.0}
        extracted_within = {"value": 100.0000001}  # 許容誤差内
        extracted_outside = {"value": 100.1}  # 許容誤差外

        calc_within = AccuracyCalculator(golden, extracted_within, tolerance=1e-6)
        accuracy_within = calc_within.calculate_field_accuracy()
        assert accuracy_within == 1.0

        calc_outside = AccuracyCalculator(golden, extracted_outside, tolerance=1e-6)
        accuracy_outside = calc_outside.calculate_field_accuracy()
        assert accuracy_outside == 0.0

    def test_string_whitespace_handling(self):
        """文字列の空白処理テスト"""
        golden = {"name": "田中太郎"}
        extracted = {"name": " 田中太郎 "}  # 前後に空白

        calculator = AccuracyCalculator(golden, extracted)
        accuracy = calculator.calculate_field_accuracy()
        assert accuracy == 1.0  # 空白はトリムされる

    def test_export_diff_report(self, golden_data, extracted_data_partial):
        """差分レポート出力テスト"""
        calculator = AccuracyCalculator(golden_data, extracted_data_partial)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "diff_report.json"
            calculator.export_diff_report(output_path)

            assert output_path.exists()

            with open(output_path, 'r', encoding='utf-8') as f:
                report = json.load(f)

            assert 'metrics' in report
            assert 'diff' in report
            assert 'generated_at' in report

    def test_empty_data(self):
        """空データの処理テスト"""
        golden = {}
        extracted = {}

        calculator = AccuracyCalculator(golden, extracted)
        accuracy = calculator.calculate_field_accuracy()
        assert accuracy == 0.0  # フィールドがないので0

    def test_deeply_nested_dict(self):
        """深くネストされた辞書のテスト"""
        golden = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": "deep"
                    }
                }
            }
        }
        extracted = golden.copy()

        calculator = AccuracyCalculator(golden, extracted)
        accuracy = calculator.calculate_field_accuracy()
        assert accuracy == 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
