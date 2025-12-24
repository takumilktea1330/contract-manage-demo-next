"""
コスト計算モジュールのテスト
"""

import pytest
import json
import tempfile
from pathlib import Path
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluators import CostCalculator


class TestCostCalculator:
    """CostCalculatorクラスのテスト"""

    @pytest.fixture
    def pricing_config(self):
        """価格設定を返す"""
        return {
            "test-model": {
                "input_token_price_per_1m": 2.0,
                "output_token_price_per_1m": 10.0,
                "currency": "USD",
                "exchange_rate": 150.0
            },
            "cheap-model": {
                "input_token_price_per_1m": 0.5,
                "output_token_price_per_1m": 1.0,
                "currency": "USD",
                "exchange_rate": 150.0
            }
        }

    @pytest.fixture
    def calculator(self, pricing_config):
        """CostCalculatorのインスタンスを返す"""
        return CostCalculator(pricing_config)

    def test_calculator_initialization_with_dict(self, pricing_config):
        """辞書での初期化テスト"""
        calculator = CostCalculator(pricing_config)
        assert calculator.pricing == pricing_config

    def test_calculator_initialization_without_config(self):
        """設定なしでの初期化テスト"""
        calculator = CostCalculator()
        assert calculator.pricing == {}

    def test_load_pricing_from_file(self, pricing_config):
        """ファイルからの価格設定読み込みテスト"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(pricing_config, f)
            config_path = f.name

        try:
            calculator = CostCalculator(config_path)
            assert calculator.pricing == pricing_config
        finally:
            Path(config_path).unlink()

    def test_load_pricing_nonexistent_file(self):
        """存在しないファイルの読み込みテスト"""
        with pytest.raises(FileNotFoundError):
            CostCalculator("nonexistent_pricing.json")

    def test_calculate_cost_usd(self, calculator):
        """USD建てコスト計算テスト"""
        cost = calculator.calculate_cost(
            model="test-model",
            input_tokens=100_000,
            output_tokens=50_000,
            currency="USD"
        )
        # 入力: 100,000 / 1,000,000 * 2.0 = 0.2 USD
        # 出力: 50,000 / 1,000,000 * 10.0 = 0.5 USD
        # 合計: 0.7 USD
        assert cost == pytest.approx(0.7, rel=1e-6)

    def test_calculate_cost_jpy(self, calculator):
        """JPY建てコスト計算テスト"""
        cost = calculator.calculate_cost(
            model="test-model",
            input_tokens=100_000,
            output_tokens=50_000,
            currency="JPY"
        )
        # 0.7 USD * 150 = 105 JPY
        assert cost == pytest.approx(105.0, rel=1e-6)

    def test_calculate_cost_unknown_model(self, calculator):
        """存在しないモデルのコスト計算テスト"""
        with pytest.raises(ValueError):
            calculator.calculate_cost(
                model="unknown-model",
                input_tokens=1000,
                output_tokens=1000
            )

    def test_calculate_cost_breakdown(self, calculator):
        """コスト内訳計算テスト"""
        breakdown = calculator.calculate_cost_breakdown(
            model="test-model",
            input_tokens=100_000,
            output_tokens=50_000,
            currency="JPY"
        )

        assert 'model' in breakdown
        assert 'input_tokens' in breakdown
        assert 'output_tokens' in breakdown
        assert 'total_tokens' in breakdown
        assert 'input_cost' in breakdown
        assert 'output_cost' in breakdown
        assert 'total_cost' in breakdown
        assert 'currency' in breakdown
        assert 'timestamp' in breakdown

        assert breakdown['model'] == "test-model"
        assert breakdown['input_tokens'] == 100_000
        assert breakdown['output_tokens'] == 50_000
        assert breakdown['total_tokens'] == 150_000
        assert breakdown['currency'] == "JPY"
        assert breakdown['total_cost'] == pytest.approx(105.0, rel=1e-6)

    def test_calculate_average_cost(self, calculator):
        """平均コスト計算テスト"""
        results = [
            {"model": "test-model", "input_tokens": 100_000, "output_tokens": 50_000},
            {"model": "test-model", "input_tokens": 200_000, "output_tokens": 100_000},
            {"model": "test-model", "input_tokens": 150_000, "output_tokens": 75_000}
        ]

        average_cost = calculator.calculate_average_cost(results, currency="USD")
        # 各コスト: 0.7, 1.4, 1.05
        # 平均: (0.7 + 1.4 + 1.05) / 3 = 1.05
        assert average_cost == pytest.approx(1.05, rel=1e-6)

    def test_calculate_average_cost_empty(self, calculator):
        """空の結果での平均コスト計算テスト"""
        average_cost = calculator.calculate_average_cost([], currency="USD")
        assert average_cost == 0.0

    def test_get_cost_summary(self, calculator):
        """コストサマリー取得テスト"""
        results = [
            {"model": "test-model", "input_tokens": 100_000, "output_tokens": 50_000},
            {"model": "cheap-model", "input_tokens": 100_000, "output_tokens": 50_000},
        ]

        summary = calculator.get_cost_summary(results, currency="USD")

        assert 'total_cost' in summary
        assert 'average_cost' in summary
        assert 'min_cost' in summary
        assert 'max_cost' in summary
        assert 'count' in summary
        assert 'total_input_tokens' in summary
        assert 'total_output_tokens' in summary
        assert 'currency' in summary

        assert summary['count'] == 2
        assert summary['total_input_tokens'] == 200_000
        assert summary['total_output_tokens'] == 100_000
        assert summary['min_cost'] < summary['max_cost']

    def test_get_cost_summary_empty(self, calculator):
        """空の結果でのコストサマリー取得テスト"""
        summary = calculator.get_cost_summary([], currency="USD")

        assert summary['total_cost'] == 0.0
        assert summary['average_cost'] == 0.0
        assert summary['count'] == 0

    def test_compare_models(self, calculator):
        """モデル比較テスト"""
        costs = calculator.compare_models(
            input_tokens=100_000,
            output_tokens=50_000,
            currency="USD"
        )

        assert isinstance(costs, dict)
        assert len(costs) == 2
        assert "test-model" in costs
        assert "cheap-model" in costs

        # cheap-model の方が安いはず
        assert costs["cheap-model"] < costs["test-model"]

        # コストの昇順でソートされているはず
        cost_values = list(costs.values())
        assert cost_values == sorted(cost_values)

    def test_compare_models_specific(self, calculator):
        """特定モデルの比較テスト"""
        costs = calculator.compare_models(
            input_tokens=100_000,
            output_tokens=50_000,
            models=["test-model"],
            currency="USD"
        )

        assert len(costs) == 1
        assert "test-model" in costs

    def test_get_pricing_info_all(self, calculator, pricing_config):
        """全モデルの価格情報取得テスト"""
        pricing_info = calculator.get_pricing_info()
        assert pricing_info == pricing_config

    def test_get_pricing_info_specific(self, calculator):
        """特定モデルの価格情報取得テスト"""
        pricing_info = calculator.get_pricing_info("test-model")
        assert "test-model" in pricing_info
        assert len(pricing_info) == 1

    def test_get_pricing_info_unknown_model(self, calculator):
        """存在しないモデルの価格情報取得テスト"""
        with pytest.raises(ValueError):
            calculator.get_pricing_info("unknown-model")

    def test_export_cost_report(self, calculator):
        """コストレポート出力テスト"""
        results = [
            {"model": "test-model", "input_tokens": 100_000, "output_tokens": 50_000},
            {"model": "cheap-model", "input_tokens": 100_000, "output_tokens": 50_000},
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "cost_report.json"
            calculator.export_cost_report(results, output_path, currency="USD")

            assert output_path.exists()

            with open(output_path, 'r', encoding='utf-8') as f:
                report = json.load(f)

            assert 'summary' in report
            assert 'details' in report
            assert 'generated_at' in report
            assert len(report['details']) == 2

    def test_large_token_count(self, calculator):
        """大量トークンでのコスト計算テスト"""
        cost = calculator.calculate_cost(
            model="test-model",
            input_tokens=10_000_000,
            output_tokens=5_000_000,
            currency="USD"
        )
        # 入力: 10M / 1M * 2.0 = 20 USD
        # 出力: 5M / 1M * 10.0 = 50 USD
        # 合計: 70 USD
        assert cost == pytest.approx(70.0, rel=1e-6)

    def test_zero_tokens(self, calculator):
        """トークン数0でのコスト計算テスト"""
        cost = calculator.calculate_cost(
            model="test-model",
            input_tokens=0,
            output_tokens=0,
            currency="USD"
        )
        assert cost == 0.0

    def test_pricing_validation(self):
        """価格設定検証テスト"""
        invalid_config = {
            "invalid-model": {
                # 必須フィールドが欠けている
                "input_token_price_per_1m": 2.0,
                # output_token_price_per_1m が欠落
            }
        }

        with pytest.raises(ValueError):
            CostCalculator(invalid_config)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
