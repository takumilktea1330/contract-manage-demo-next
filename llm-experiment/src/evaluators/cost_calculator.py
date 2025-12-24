"""
コスト計算モジュール

トークン数とトークン単価からコストを計算する。
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class CostCalculator:
    """APIコストを計算するクラス"""

    def __init__(self, pricing_config: Optional[Union[str, Dict, Path]] = None):
        """
        CostCalculatorの初期化

        Args:
            pricing_config: 価格設定（ファイルパス、辞書、またはPathオブジェクト）
        """
        self.pricing = {}

        if pricing_config is not None:
            self.load_pricing(pricing_config)

    def load_pricing(self, pricing_config: Union[str, Dict, Path]) -> None:
        """
        価格設定を読み込む

        Args:
            pricing_config: 価格設定（ファイルパス、辞書、またはPathオブジェクト）

        Raises:
            FileNotFoundError: 設定ファイルが存在しない場合
            ValueError: 設定が無効な場合
        """
        try:
            # 辞書の場合
            if isinstance(pricing_config, dict):
                self.pricing = pricing_config
                logger.info("価格設定を辞書から読み込みました")

            # ファイルパスの場合
            elif isinstance(pricing_config, (str, Path)):
                config_path = Path(pricing_config)
                if not config_path.exists():
                    raise FileNotFoundError(f"価格設定ファイルが見つかりません: {config_path}")

                with open(config_path, 'r', encoding='utf-8') as f:
                    self.pricing = json.load(f)
                logger.info(f"価格設定を読み込みました: {config_path}")

            else:
                raise ValueError(f"サポートされていない設定の型: {type(pricing_config)}")

            # 設定の検証
            self._validate_pricing()

        except json.JSONDecodeError as e:
            logger.error(f"価格設定のJSONパースに失敗しました: {str(e)}")
            raise ValueError(f"価格設定のJSONが無効です: {str(e)}")
        except Exception as e:
            logger.error(f"価格設定の読み込みに失敗しました: {str(e)}")
            raise

    def _validate_pricing(self) -> None:
        """価格設定の妥当性を検証する"""
        for model, config in self.pricing.items():
            required_keys = ['input_token_price_per_1m', 'output_token_price_per_1m']
            for key in required_keys:
                if key not in config:
                    raise ValueError(f"モデル '{model}' の価格設定に '{key}' がありません")

            # デフォルト値の設定
            if 'currency' not in config:
                config['currency'] = 'USD'
            if 'exchange_rate' not in config:
                config['exchange_rate'] = 1.0

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        currency: str = 'JPY'
    ) -> float:
        """
        トークン数とトークン単価からコストを計算する

        Args:
            model: モデル名
            input_tokens: 入力トークン数
            output_tokens: 出力トークン数
            currency: 出力通貨（'JPY' または 'USD'）

        Returns:
            コスト（指定通貨）

        Raises:
            ValueError: モデルが価格設定に存在しない場合
        """
        if model not in self.pricing:
            raise ValueError(f"モデル '{model}' の価格設定が見つかりません")

        config = self.pricing[model]

        # 1Mトークンあたりの価格
        input_price_per_1m = config['input_token_price_per_1m']
        output_price_per_1m = config['output_token_price_per_1m']

        # コスト計算（元通貨）
        input_cost = (input_tokens / 1_000_000) * input_price_per_1m
        output_cost = (output_tokens / 1_000_000) * output_price_per_1m
        total_cost = input_cost + output_cost

        # 通貨変換
        if currency == 'JPY' and config['currency'] == 'USD':
            total_cost *= config['exchange_rate']
        elif currency == 'USD' and config['currency'] == 'JPY':
            total_cost /= config['exchange_rate']

        logger.info(
            f"コスト計算: {model}, "
            f"入力={input_tokens:,}トークン, "
            f"出力={output_tokens:,}トークン, "
            f"コスト={total_cost:.2f}{currency}"
        )

        return total_cost

    def calculate_cost_breakdown(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        currency: str = 'JPY'
    ) -> Dict:
        """
        コストの内訳を計算する

        Args:
            model: モデル名
            input_tokens: 入力トークン数
            output_tokens: 出力トークン数
            currency: 出力通貨

        Returns:
            コスト内訳の辞書
        """
        if model not in self.pricing:
            raise ValueError(f"モデル '{model}' の価格設定が見つかりません")

        config = self.pricing[model]

        # 1Mトークンあたりの価格
        input_price_per_1m = config['input_token_price_per_1m']
        output_price_per_1m = config['output_token_price_per_1m']

        # 元通貨でのコスト
        input_cost_original = (input_tokens / 1_000_000) * input_price_per_1m
        output_cost_original = (output_tokens / 1_000_000) * output_price_per_1m
        total_cost_original = input_cost_original + output_cost_original

        # 為替レート
        exchange_rate = config.get('exchange_rate', 1.0)
        original_currency = config.get('currency', 'USD')

        # 通貨変換
        if currency == 'JPY' and original_currency == 'USD':
            input_cost = input_cost_original * exchange_rate
            output_cost = output_cost_original * exchange_rate
            total_cost = total_cost_original * exchange_rate
        elif currency == 'USD' and original_currency == 'JPY':
            input_cost = input_cost_original / exchange_rate
            output_cost = output_cost_original / exchange_rate
            total_cost = total_cost_original / exchange_rate
        else:
            input_cost = input_cost_original
            output_cost = output_cost_original
            total_cost = total_cost_original

        breakdown = {
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': input_tokens + output_tokens,
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': total_cost,
            'currency': currency,
            'original_currency': original_currency,
            'exchange_rate': exchange_rate,
            'timestamp': datetime.now().isoformat()
        }

        return breakdown

    def calculate_average_cost(
        self,
        results: List[Dict],
        currency: str = 'JPY'
    ) -> float:
        """
        平均コスト/PDFを算出する

        Args:
            results: コスト計算結果のリスト
                各要素は {'model': str, 'input_tokens': int, 'output_tokens': int} の形式
            currency: 出力通貨

        Returns:
            平均コスト
        """
        if not results:
            logger.warning("結果が空です")
            return 0.0

        total_cost = 0.0
        for result in results:
            cost = self.calculate_cost(
                result['model'],
                result['input_tokens'],
                result['output_tokens'],
                currency
            )
            total_cost += cost

        average_cost = total_cost / len(results)

        logger.info(
            f"平均コスト: {average_cost:.2f}{currency} "
            f"(合計: {total_cost:.2f}{currency}, {len(results)}件)"
        )

        return average_cost

    def get_cost_summary(
        self,
        results: List[Dict],
        currency: str = 'JPY'
    ) -> Dict:
        """
        コストの統計サマリーを取得する

        Args:
            results: コスト計算結果のリスト
            currency: 出力通貨

        Returns:
            コストサマリーの辞書
        """
        if not results:
            return {
                'total_cost': 0.0,
                'average_cost': 0.0,
                'min_cost': 0.0,
                'max_cost': 0.0,
                'count': 0,
                'currency': currency
            }

        costs = []
        total_input_tokens = 0
        total_output_tokens = 0

        for result in results:
            cost = self.calculate_cost(
                result['model'],
                result['input_tokens'],
                result['output_tokens'],
                currency
            )
            costs.append(cost)
            total_input_tokens += result['input_tokens']
            total_output_tokens += result['output_tokens']

        summary = {
            'total_cost': sum(costs),
            'average_cost': sum(costs) / len(costs),
            'min_cost': min(costs),
            'max_cost': max(costs),
            'count': len(costs),
            'total_input_tokens': total_input_tokens,
            'total_output_tokens': total_output_tokens,
            'total_tokens': total_input_tokens + total_output_tokens,
            'currency': currency,
            'timestamp': datetime.now().isoformat()
        }

        logger.info(
            f"コストサマリー: 合計={summary['total_cost']:.2f}{currency}, "
            f"平均={summary['average_cost']:.2f}{currency}, "
            f"最小={summary['min_cost']:.2f}{currency}, "
            f"最大={summary['max_cost']:.2f}{currency}"
        )

        return summary

    def compare_models(
        self,
        input_tokens: int,
        output_tokens: int,
        models: Optional[List[str]] = None,
        currency: str = 'JPY'
    ) -> Dict[str, float]:
        """
        複数モデルのコストを比較する

        Args:
            input_tokens: 入力トークン数
            output_tokens: 出力トークン数
            models: 比較するモデルのリスト（Noneの場合は全モデル）
            currency: 出力通貨

        Returns:
            モデル名とコストの辞書（コストの昇順）
        """
        if models is None:
            models = list(self.pricing.keys())

        costs = {}
        for model in models:
            if model in self.pricing:
                cost = self.calculate_cost(model, input_tokens, output_tokens, currency)
                costs[model] = cost
            else:
                logger.warning(f"モデル '{model}' の価格設定が見つかりません")

        # コストの昇順でソート
        sorted_costs = dict(sorted(costs.items(), key=lambda x: x[1]))

        logger.info(f"モデル比較: {len(sorted_costs)}モデル")
        for model, cost in sorted_costs.items():
            logger.info(f"  {model}: {cost:.2f}{currency}")

        return sorted_costs

    def get_pricing_info(self, model: Optional[str] = None) -> Dict:
        """
        価格設定情報を取得する

        Args:
            model: モデル名（Noneの場合は全モデル）

        Returns:
            価格設定情報の辞書
        """
        if model is not None:
            if model not in self.pricing:
                raise ValueError(f"モデル '{model}' の価格設定が見つかりません")
            return {model: self.pricing[model]}

        return self.pricing.copy()

    def export_cost_report(
        self,
        results: List[Dict],
        output_path: Union[str, Path],
        currency: str = 'JPY'
    ) -> None:
        """
        コストレポートをJSONファイルとして出力する

        Args:
            results: コスト計算結果のリスト
            output_path: 出力ファイルパス
            currency: 出力通貨
        """
        summary = self.get_cost_summary(results, currency)

        # 各結果の詳細を追加
        detailed_results = []
        for result in results:
            breakdown = self.calculate_cost_breakdown(
                result['model'],
                result['input_tokens'],
                result['output_tokens'],
                currency
            )
            # 元の結果に追加情報があればマージ
            breakdown.update({k: v for k, v in result.items()
                            if k not in breakdown})
            detailed_results.append(breakdown)

        report = {
            'summary': summary,
            'details': detailed_results,
            'generated_at': datetime.now().isoformat()
        }

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"コストレポートを出力しました: {output_path}")
