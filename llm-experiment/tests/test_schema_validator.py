"""
スキーマ検証モジュールのテスト
"""

import pytest
import json
import tempfile
from pathlib import Path
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluators import SchemaValidator


class TestSchemaValidator:
    """SchemaValidatorクラスのテスト"""

    @pytest.fixture
    def simple_schema(self):
        """シンプルなJSONスキーマを返す"""
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "email": {"type": "string", "format": "email"}
            },
            "required": ["name", "age"]
        }

    @pytest.fixture
    def validator(self, simple_schema):
        """SchemaValidatorのインスタンスを返す"""
        return SchemaValidator(simple_schema)

    def test_validator_initialization_with_dict(self, simple_schema):
        """辞書でのバリデータ初期化テスト"""
        validator = SchemaValidator(simple_schema)
        assert validator.schema is not None
        assert validator.validator is not None

    def test_validator_initialization_without_schema(self):
        """スキーマなしでのバリデータ初期化テスト"""
        validator = SchemaValidator()
        assert validator.schema is None
        assert validator.validator is None

    def test_validate_valid_data(self, validator):
        """正常なデータの検証テスト"""
        valid_data = {
            "name": "田中太郎",
            "age": 30,
            "email": "tanaka@example.com"
        }
        is_valid, errors = validator.validate(valid_data)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_missing_required_field(self, validator):
        """必須フィールド欠落の検証テスト"""
        invalid_data = {
            "name": "田中太郎"
            # ageが欠落
        }
        is_valid, errors = validator.validate(invalid_data)
        assert is_valid is False
        assert len(errors) > 0
        assert any("age" in error.lower() for error in errors)

    def test_validate_wrong_type(self, validator):
        """型が誤っているデータの検証テスト"""
        invalid_data = {
            "name": "田中太郎",
            "age": "thirty"  # 文字列（本来はinteger）
        }
        is_valid, errors = validator.validate(invalid_data)
        assert is_valid is False
        assert len(errors) > 0

    def test_validate_json_string(self, validator):
        """JSON文字列の検証テスト"""
        valid_json_str = '{"name": "田中太郎", "age": 30}'
        is_valid, errors = validator.validate(valid_json_str)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_invalid_json_string(self, validator):
        """無効なJSON文字列の検証テスト"""
        invalid_json_str = '{"name": "田中太郎", age: 30}'  # JSONとして無効
        is_valid, errors = validator.validate(invalid_json_str)
        assert is_valid is False
        assert len(errors) > 0
        assert any("JSON" in error for error in errors)

    def test_validate_without_schema_loaded(self):
        """スキーマ未読み込みでの検証テスト"""
        validator = SchemaValidator()
        with pytest.raises(ValueError):
            validator.validate({"name": "test"})

    def test_load_schema_from_file(self, simple_schema):
        """ファイルからのスキーマ読み込みテスト"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(simple_schema, f)
            schema_path = f.name

        try:
            validator = SchemaValidator(schema_path)
            assert validator.schema is not None
            assert validator.schema == simple_schema
        finally:
            Path(schema_path).unlink()

    def test_load_schema_nonexistent_file(self):
        """存在しないファイルの読み込みテスト"""
        with pytest.raises(FileNotFoundError):
            SchemaValidator("nonexistent_schema.json")

    def test_calculate_conformance_rate(self, validator):
        """スキーマ準拠率の計算テスト"""
        results = [
            (True, []),
            (True, []),
            (False, ["error1"]),
            (True, []),
            (False, ["error2"])
        ]
        conformance_rate = validator.calculate_conformance_rate(results)
        assert conformance_rate == 0.6  # 5件中3件が有効

    def test_calculate_conformance_rate_empty(self, validator):
        """空の結果でのスキーマ準拠率計算テスト"""
        conformance_rate = validator.calculate_conformance_rate([])
        assert conformance_rate == 0.0

    def test_get_schema_summary(self, validator):
        """スキーマ概要取得テスト"""
        summary = validator.get_schema_summary()
        assert isinstance(summary, dict)
        assert summary['type'] == 'object'
        assert summary['required_fields'] == 2

    def test_check_required_fields(self, validator):
        """必須フィールドチェックテスト"""
        data_with_all = {"name": "田中太郎", "age": 30}
        all_present, missing = validator.check_required_fields(data_with_all)
        assert all_present is True
        assert len(missing) == 0

        data_with_missing = {"name": "田中太郎"}
        all_present, missing = validator.check_required_fields(data_with_missing)
        assert all_present is False
        assert "age" in missing

    def test_validate_batch(self, validator):
        """バッチ検証テスト"""
        data_list = [
            {"name": "田中太郎", "age": 30},
            {"name": "佐藤花子", "age": 25},
            {"name": "鈴木一郎"},  # age欠落
            {"name": "高橋次郎", "age": 35}
        ]
        results = validator.validate_batch(data_list)
        assert len(results) == 4
        assert results[0][0] is True  # 1件目は有効
        assert results[1][0] is True  # 2件目は有効
        assert results[2][0] is False  # 3件目は無効
        assert results[3][0] is True  # 4件目は有効

    def test_validate_batch_stop_on_error(self, validator):
        """エラー時停止付きバッチ検証テスト"""
        data_list = [
            {"name": "田中太郎", "age": 30},
            {"name": "佐藤花子"},  # age欠落
            {"name": "鈴木一郎", "age": 40}
        ]
        results = validator.validate_batch(data_list, stop_on_error=True)
        assert len(results) == 2  # エラーで停止するため2件まで

    def test_validate_with_details(self, validator):
        """詳細付き検証テスト"""
        data = {"name": "田中太郎", "age": 30}
        result = validator.validate_with_details(data)
        assert isinstance(result, dict)
        assert 'is_valid' in result
        assert 'error_count' in result
        assert 'errors' in result
        assert 'data_keys' in result
        assert result['is_valid'] is True
        assert result['error_count'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
