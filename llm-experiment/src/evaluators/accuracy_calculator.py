"""
精度計算モジュール

正解データ（Golden Standard）と抽出データを比較し、
項目正答率、F1スコア、完全一致率を計算する。
"""

import json
import logging
from typing import Dict, List, Tuple, Any, Union, Set
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class AccuracyCalculator:
    """データ抽出精度を計算するクラス"""

    def __init__(
        self,
        golden_data: Union[Dict, str, Path],
        extracted_data: Union[Dict, str, Path],
        tolerance: float = 1e-6
    ):
        """
        AccuracyCalculatorの初期化

        Args:
            golden_data: 正解データ（辞書、JSON文字列、またはファイルパス）
            extracted_data: 抽出データ（辞書、JSON文字列、またはファイルパス）
            tolerance: 数値比較時の許容誤差
        """
        self.golden_data = self._load_data(golden_data, "golden")
        self.extracted_data = self._load_data(extracted_data, "extracted")
        self.tolerance = tolerance

        # 比較結果のキャッシュ
        self._comparison_cache = None

    def _load_data(self, data: Union[Dict, str, Path], data_type: str) -> Dict:
        """
        データを読み込む

        Args:
            data: データ（辞書、JSON文字列、またはファイルパス）
            data_type: データの種類（ログ用）

        Returns:
            辞書形式のデータ
        """
        try:
            # 辞書の場合
            if isinstance(data, dict):
                return data

            # ファイルパスの場合
            if isinstance(data, Path) or (isinstance(data, str) and Path(data).exists()):
                with open(data, 'r', encoding='utf-8') as f:
                    return json.load(f)

            # JSON文字列の場合
            if isinstance(data, str):
                return json.loads(data)

            raise ValueError(f"サポートされていないデータ型: {type(data)}")

        except json.JSONDecodeError as e:
            logger.error(f"{data_type}データのJSONパースに失敗: {str(e)}")
            raise ValueError(f"{data_type}データのJSONが無効です: {str(e)}")
        except Exception as e:
            logger.error(f"{data_type}データの読み込みに失敗: {str(e)}")
            raise

    def _compare_values(self, golden_val: Any, extracted_val: Any, path: str = "") -> bool:
        """
        2つの値を比較する

        Args:
            golden_val: 正解値
            extracted_val: 抽出値
            path: 現在のパス（デバッグ用）

        Returns:
            値が一致するか
        """
        # None/null の処理
        if golden_val is None and extracted_val is None:
            return True
        if golden_val is None or extracted_val is None:
            return False

        # 型が異なる場合
        if type(golden_val) != type(extracted_val):
            # 数値型同士の比較は許容
            if isinstance(golden_val, (int, float)) and isinstance(extracted_val, (int, float)):
                return abs(float(golden_val) - float(extracted_val)) < self.tolerance
            return False

        # 数値の比較
        if isinstance(golden_val, (int, float)):
            return abs(golden_val - extracted_val) < self.tolerance

        # 文字列の比較
        if isinstance(golden_val, str):
            return golden_val.strip() == extracted_val.strip()

        # ブール値の比較
        if isinstance(golden_val, bool):
            return golden_val == extracted_val

        # リストの比較
        if isinstance(golden_val, list):
            if len(golden_val) != len(extracted_val):
                return False
            # 順序を考慮した比較（デフォルト）
            return all(
                self._compare_values(g, e, f"{path}[{i}]")
                for i, (g, e) in enumerate(zip(golden_val, extracted_val))
            )

        # 辞書の比較
        if isinstance(golden_val, dict):
            return self._compare_dicts(golden_val, extracted_val, path)

        # その他
        return golden_val == extracted_val

    def _compare_dicts(self, golden_dict: Dict, extracted_dict: Dict, path: str = "") -> bool:
        """
        2つの辞書を比較する

        Args:
            golden_dict: 正解辞書
            extracted_dict: 抽出辞書
            path: 現在のパス

        Returns:
            辞書が一致するか
        """
        # キーの数が異なる場合
        if set(golden_dict.keys()) != set(extracted_dict.keys()):
            return False

        # 各キーの値を比較
        for key in golden_dict.keys():
            new_path = f"{path}.{key}" if path else key
            if not self._compare_values(golden_dict[key], extracted_dict[key], new_path):
                return False

        return True

    def calculate_field_accuracy(self) -> float:
        """
        項目正答率を計算する
        正解JSONの総フィールド数に対し、正しく抽出されたフィールドの割合

        Returns:
            項目正答率（0.0〜1.0）
        """
        comparison = self._get_comparison_result()

        total_fields = comparison['total_fields']
        correct_fields = comparison['correct_fields']

        if total_fields == 0:
            logger.warning("フィールドが存在しません")
            return 0.0

        accuracy = correct_fields / total_fields
        logger.info(f"項目正答率: {accuracy:.2%} ({correct_fields}/{total_fields})")

        return accuracy

    def calculate_f1_score(self) -> float:
        """
        F1スコアを計算する
        各キー・バリューペアを要素とみなし、適合率と再現率からF1スコアを算出

        Returns:
            F1スコア（0.0〜1.0）
        """
        comparison = self._get_comparison_result()

        true_positive = comparison['correct_fields']  # 正しく抽出されたフィールド
        false_positive = comparison['extra_fields']    # 余分なフィールド
        false_negative = comparison['missing_fields']  # 不足しているフィールド

        # 適合率（Precision）
        if true_positive + false_positive == 0:
            precision = 0.0
        else:
            precision = true_positive / (true_positive + false_positive)

        # 再現率（Recall）
        if true_positive + false_negative == 0:
            recall = 0.0
        else:
            recall = true_positive / (true_positive + false_negative)

        # F1スコア
        if precision + recall == 0:
            f1_score = 0.0
        else:
            f1_score = 2 * (precision * recall) / (precision + recall)

        logger.info(
            f"F1スコア: {f1_score:.4f} "
            f"(Precision: {precision:.4f}, Recall: {recall:.4f})"
        )

        return f1_score

    def calculate_exact_match(self) -> bool:
        """
        完全一致率を計算する
        LLMの出力JSONが正解JSONと文字列として完全に一致するか

        Returns:
            完全一致するか
        """
        # JSON文字列として正規化して比較
        golden_str = json.dumps(self.golden_data, sort_keys=True, ensure_ascii=False)
        extracted_str = json.dumps(self.extracted_data, sort_keys=True, ensure_ascii=False)

        exact_match = golden_str == extracted_str

        logger.info(f"完全一致: {exact_match}")
        return exact_match

    def _get_comparison_result(self) -> Dict:
        """
        詳細な比較結果を取得する（キャッシュあり）

        Returns:
            比較結果の辞書
        """
        if self._comparison_cache is not None:
            return self._comparison_cache

        result = self.compare_nested_dict(self.golden_data, self.extracted_data)
        self._comparison_cache = result
        return result

    def compare_nested_dict(
        self,
        golden: Dict,
        extracted: Dict,
        path: str = ""
    ) -> Dict:
        """
        ネストされた辞書を再帰的に比較する

        Args:
            golden: 正解辞書
            extracted: 抽出辞書
            path: 現在のパス

        Returns:
            比較結果の辞書
        """
        result = {
            'total_fields': 0,
            'correct_fields': 0,
            'incorrect_fields': 0,
            'missing_fields': 0,
            'extra_fields': 0,
            'field_details': []
        }

        # 正解データの全フィールドをカウント
        golden_fields = self._flatten_dict(golden)
        extracted_fields = self._flatten_dict(extracted)

        result['total_fields'] = len(golden_fields)

        # 各フィールドを比較
        for field_path, golden_value in golden_fields.items():
            if field_path not in extracted_fields:
                # フィールドが存在しない
                result['missing_fields'] += 1
                result['field_details'].append({
                    'path': field_path,
                    'status': 'missing',
                    'golden_value': golden_value,
                    'extracted_value': None
                })
            elif self._compare_values(golden_value, extracted_fields[field_path], field_path):
                # 値が一致
                result['correct_fields'] += 1
                result['field_details'].append({
                    'path': field_path,
                    'status': 'correct',
                    'golden_value': golden_value,
                    'extracted_value': extracted_fields[field_path]
                })
            else:
                # 値が不一致
                result['incorrect_fields'] += 1
                result['field_details'].append({
                    'path': field_path,
                    'status': 'incorrect',
                    'golden_value': golden_value,
                    'extracted_value': extracted_fields[field_path]
                })

        # 余分なフィールドをカウント
        for field_path, extracted_value in extracted_fields.items():
            if field_path not in golden_fields:
                result['extra_fields'] += 1
                result['field_details'].append({
                    'path': field_path,
                    'status': 'extra',
                    'golden_value': None,
                    'extracted_value': extracted_value
                })

        return result

    def _flatten_dict(
        self,
        data: Any,
        parent_key: str = "",
        separator: str = "."
    ) -> Dict[str, Any]:
        """
        ネストされた辞書をフラットにする

        Args:
            data: データ
            parent_key: 親キー
            separator: セパレータ

        Returns:
            フラット化された辞書
        """
        items = {}

        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{parent_key}{separator}{key}" if parent_key else key

                if isinstance(value, dict):
                    items.update(self._flatten_dict(value, new_key, separator))
                elif isinstance(value, list):
                    # リストの各要素を展開
                    for i, item in enumerate(value):
                        list_key = f"{new_key}[{i}]"
                        if isinstance(item, dict):
                            items.update(self._flatten_dict(item, list_key, separator))
                        else:
                            items[list_key] = item
                else:
                    items[new_key] = value

        elif isinstance(data, list):
            for i, item in enumerate(data):
                list_key = f"{parent_key}[{i}]"
                if isinstance(item, dict):
                    items.update(self._flatten_dict(item, list_key, separator))
                else:
                    items[list_key] = item
        else:
            items[parent_key] = data

        return items

    def get_detailed_diff(self) -> Dict:
        """
        差分の詳細を取得する

        Returns:
            詳細な差分情報の辞書
        """
        comparison = self._get_comparison_result()

        diff = {
            'summary': {
                'total_fields': comparison['total_fields'],
                'correct_fields': comparison['correct_fields'],
                'incorrect_fields': comparison['incorrect_fields'],
                'missing_fields': comparison['missing_fields'],
                'extra_fields': comparison['extra_fields'],
            },
            'correct': [
                detail for detail in comparison['field_details']
                if detail['status'] == 'correct'
            ],
            'incorrect': [
                detail for detail in comparison['field_details']
                if detail['status'] == 'incorrect'
            ],
            'missing': [
                detail for detail in comparison['field_details']
                if detail['status'] == 'missing'
            ],
            'extra': [
                detail for detail in comparison['field_details']
                if detail['status'] == 'extra'
            ]
        }

        return diff

    def get_metrics(self) -> Dict:
        """
        全ての評価指標を一度に計算する

        Returns:
            評価指標の辞書
        """
        metrics = {
            'field_accuracy': self.calculate_field_accuracy(),
            'f1_score': self.calculate_f1_score(),
            'exact_match': self.calculate_exact_match(),
            'timestamp': datetime.now().isoformat()
        }

        # 詳細統計を追加
        comparison = self._get_comparison_result()
        metrics['statistics'] = {
            'total_fields': comparison['total_fields'],
            'correct_fields': comparison['correct_fields'],
            'incorrect_fields': comparison['incorrect_fields'],
            'missing_fields': comparison['missing_fields'],
            'extra_fields': comparison['extra_fields'],
        }

        logger.info(f"評価指標計算完了: 項目正答率={metrics['field_accuracy']:.2%}, "
                   f"F1スコア={metrics['f1_score']:.4f}, "
                   f"完全一致={metrics['exact_match']}")

        return metrics

    def export_diff_report(self, output_path: Union[str, Path]) -> None:
        """
        差分レポートをJSONファイルとして出力する

        Args:
            output_path: 出力ファイルパス
        """
        diff = self.get_detailed_diff()
        metrics = self.get_metrics()

        report = {
            'metrics': metrics,
            'diff': diff,
            'generated_at': datetime.now().isoformat()
        }

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"差分レポートを出力しました: {output_path}")
