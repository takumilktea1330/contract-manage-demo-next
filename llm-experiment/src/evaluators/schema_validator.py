"""
スキーマ検証モジュール

JSONスキーマに基づいてLLMの出力JSONを検証する。
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
import jsonschema
from jsonschema import validate, ValidationError, Draft7Validator

logger = logging.getLogger(__name__)


class SchemaValidator:
    """JSONスキーマの検証を行うクラス"""

    def __init__(self, schema: Optional[Union[str, Dict, Path]] = None):
        """
        SchemaValidatorの初期化

        Args:
            schema: JSONスキーマ（ファイルパス、辞書、またはPathオブジェクト）
        """
        self.schema = None
        self.validator = None

        if schema is not None:
            self.load_schema(schema)

    def load_schema(self, schema: Union[str, Dict, Path]) -> None:
        """
        JSONスキーマを読み込む

        Args:
            schema: JSONスキーマ（ファイルパス、辞書、またはPathオブジェクト）

        Raises:
            FileNotFoundError: スキーマファイルが存在しない場合
            ValueError: スキーマが無効な場合
        """
        try:
            # 辞書の場合
            if isinstance(schema, dict):
                self.schema = schema
                logger.info("スキーマを辞書から読み込みました")

            # ファイルパスの場合
            elif isinstance(schema, (str, Path)):
                schema_path = Path(schema)
                if not schema_path.exists():
                    raise FileNotFoundError(f"スキーマファイルが見つかりません: {schema_path}")

                with open(schema_path, 'r', encoding='utf-8') as f:
                    self.schema = json.load(f)
                logger.info(f"スキーマを読み込みました: {schema_path}")

            else:
                raise ValueError(f"サポートされていないスキーマの型: {type(schema)}")

            # バリデータの作成
            self.validator = Draft7Validator(self.schema)
            logger.info("スキーマバリデータを作成しました")

        except json.JSONDecodeError as e:
            logger.error(f"スキーマのJSONパースに失敗しました: {str(e)}")
            raise ValueError(f"スキーマのJSONが無効です: {str(e)}")
        except Exception as e:
            logger.error(f"スキーマの読み込みに失敗しました: {str(e)}")
            raise

    def validate(self, data: Union[Dict, str]) -> Tuple[bool, List[str]]:
        """
        データをスキーマに対して検証する

        Args:
            data: 検証するデータ（辞書またはJSON文字列）

        Returns:
            (検証結果, エラーメッセージのリスト)
            検証成功時は (True, [])、失敗時は (False, [エラー1, エラー2, ...])

        Raises:
            ValueError: スキーマが読み込まれていない場合
        """
        if self.schema is None or self.validator is None:
            raise ValueError("スキーマが読み込まれていません。load_schema()を先に実行してください。")

        try:
            # JSON文字列の場合はパース
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    error_msg = f"JSONパースエラー: {str(e)}"
                    logger.error(error_msg)
                    return False, [error_msg]

            # 検証実行
            errors = list(self.validator.iter_errors(data))

            if not errors:
                logger.info("スキーマ検証成功")
                return True, []

            # エラーメッセージを整形
            error_messages = []
            for error in errors:
                path = ".".join(str(p) for p in error.path) if error.path else "root"
                message = f"[{path}] {error.message}"
                error_messages.append(message)
                logger.warning(f"スキーマ検証エラー: {message}")

            return False, error_messages

        except Exception as e:
            error_msg = f"検証中に予期しないエラーが発生しました: {str(e)}"
            logger.error(error_msg)
            return False, [error_msg]

    def validate_file(self, file_path: Union[str, Path]) -> Tuple[bool, List[str]]:
        """
        JSONファイルをスキーマに対して検証する

        Args:
            file_path: JSONファイルのパス

        Returns:
            (検証結果, エラーメッセージのリスト)
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False, [f"ファイルが見つかりません: {file_path}"]

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return self.validate(data)

        except json.JSONDecodeError as e:
            error_msg = f"JSONパースエラー: {str(e)}"
            logger.error(error_msg)
            return False, [error_msg]
        except Exception as e:
            error_msg = f"ファイル検証エラー: {str(e)}"
            logger.error(error_msg)
            return False, [error_msg]

    def calculate_conformance_rate(
        self,
        results: List[Tuple[bool, List[str]]]
    ) -> float:
        """
        複数の検証結果からスキーマ準拠率を計算する

        Args:
            results: 検証結果のリスト [(is_valid, errors), ...]

        Returns:
            スキーマ準拠率（0.0〜1.0）
        """
        if not results:
            return 0.0

        valid_count = sum(1 for is_valid, _ in results if is_valid)
        conformance_rate = valid_count / len(results)

        logger.info(f"スキーマ準拠率: {conformance_rate:.2%} ({valid_count}/{len(results)})")
        return conformance_rate

    def get_schema_summary(self) -> Dict:
        """
        スキーマの概要情報を取得する

        Returns:
            スキーマの概要情報の辞書
        """
        if self.schema is None:
            return {}

        def count_properties(obj, depth=0):
            """再帰的にプロパティ数をカウント"""
            if not isinstance(obj, dict):
                return 0

            count = 0
            if 'properties' in obj:
                count += len(obj['properties'])
                for prop in obj['properties'].values():
                    count += count_properties(prop, depth + 1)

            if 'items' in obj:
                count += count_properties(obj['items'], depth + 1)

            return count

        summary = {
            'type': self.schema.get('type', 'unknown'),
            'title': self.schema.get('title', ''),
            'description': self.schema.get('description', ''),
            'total_properties': count_properties(self.schema),
            'required_fields': len(self.schema.get('required', [])),
        }

        return summary

    def validate_with_details(self, data: Union[Dict, str]) -> Dict:
        """
        詳細な検証結果を返す

        Args:
            data: 検証するデータ

        Returns:
            詳細な検証結果の辞書
        """
        is_valid, error_messages = self.validate(data)

        # データ型の確認
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except:
                data = {}

        result = {
            'is_valid': is_valid,
            'error_count': len(error_messages),
            'errors': error_messages,
            'data_keys': list(data.keys()) if isinstance(data, dict) else [],
            'validation_timestamp': self._get_timestamp()
        }

        return result

    def _get_timestamp(self) -> str:
        """現在のタイムスタンプを取得"""
        from datetime import datetime
        return datetime.now().isoformat()

    def check_required_fields(self, data: Dict) -> Tuple[bool, List[str]]:
        """
        必須フィールドが存在するか確認する

        Args:
            data: 確認するデータ

        Returns:
            (全て存在するか, 不足しているフィールドのリスト)
        """
        if self.schema is None:
            raise ValueError("スキーマが読み込まれていません")

        required_fields = self.schema.get('required', [])
        if not required_fields:
            return True, []

        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            logger.warning(f"不足している必須フィールド: {missing_fields}")
            return False, missing_fields
        else:
            logger.info("全ての必須フィールドが存在します")
            return True, []

    def validate_batch(
        self,
        data_list: List[Union[Dict, str]],
        stop_on_error: bool = False
    ) -> List[Tuple[bool, List[str]]]:
        """
        複数のデータを一括検証する

        Args:
            data_list: 検証するデータのリスト
            stop_on_error: エラー時に停止するか

        Returns:
            検証結果のリスト
        """
        results = []

        for i, data in enumerate(data_list):
            logger.info(f"検証中: {i + 1}/{len(data_list)}")
            is_valid, errors = self.validate(data)
            results.append((is_valid, errors))

            if not is_valid and stop_on_error:
                logger.warning(f"エラーが発生したため検証を停止しました ({i + 1}/{len(data_list)})")
                break

        valid_count = sum(1 for is_valid, _ in results if is_valid)
        logger.info(f"一括検証完了: {valid_count}/{len(results)} 件が有効")

        return results
