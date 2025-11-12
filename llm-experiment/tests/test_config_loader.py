"""
設定読み込みモジュールのテスト
"""

import pytest
import json
import tempfile
from pathlib import Path
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import ConfigLoader


class TestConfigLoader:
    """ConfigLoaderクラスのテスト"""

    @pytest.fixture
    def config_dir(self):
        """一時設定ディレクトリを作成"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def loader(self, config_dir):
        """ConfigLoaderのインスタンスを返す"""
        return ConfigLoader(str(config_dir))

    def test_loader_initialization(self, loader, config_dir):
        """初期化テスト"""
        assert loader is not None
        assert loader.config_dir == config_dir

    def test_load_api_keys_from_file(self, loader, config_dir):
        """ファイルからAPIキーを読み込むテスト"""
        api_keys = {
            "gemini": "test_gemini_key",
            "openai": "test_openai_key",
            "anthropic": "test_anthropic_key"
        }

        # ファイル作成
        api_keys_path = config_dir / "api_keys.json"
        with open(api_keys_path, 'w') as f:
            json.dump(api_keys, f)

        # 読み込み
        loaded_keys = loader.load_api_keys()

        assert loaded_keys == api_keys

    def test_load_api_keys_from_env(self, loader, config_dir, monkeypatch):
        """環境変数からAPIキーを読み込むテスト"""
        # 環境変数を設定
        monkeypatch.setenv('GEMINI_API_KEY', 'env_gemini_key')
        monkeypatch.setenv('OPENAI_API_KEY', 'env_openai_key')

        # ファイルが存在しない場合は環境変数から読み込む
        loaded_keys = loader.load_api_keys()

        assert 'gemini' in loaded_keys
        assert loaded_keys['gemini'] == 'env_gemini_key'

    def test_load_pricing(self, loader, config_dir):
        """価格設定を読み込むテスト"""
        pricing = {
            "test-model": {
                "input_token_price_per_1m": 2.0,
                "output_token_price_per_1m": 10.0,
                "currency": "USD",
                "exchange_rate": 150.0
            }
        }

        # ファイル作成
        pricing_path = config_dir / "pricing.json"
        with open(pricing_path, 'w') as f:
            json.dump(pricing, f)

        # 読み込み
        loaded_pricing = loader.load_pricing()

        assert loaded_pricing == pricing

    def test_load_pricing_not_found(self, loader):
        """価格設定ファイルが存在しない場合のテスト"""
        with pytest.raises(FileNotFoundError):
            loader.load_pricing()

    def test_load_schema(self, loader, config_dir):
        """スキーマを読み込むテスト"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }

        # ファイル作成
        schema_path = config_dir / "schema.json"
        with open(schema_path, 'w') as f:
            json.dump(schema, f)

        # 読み込み
        loaded_schema = loader.load_schema()

        assert loaded_schema == schema

    def test_load_schema_not_found(self, loader):
        """スキーマファイルが存在しない場合のテスト"""
        # 空の辞書が返される
        loaded_schema = loader.load_schema()
        assert loaded_schema == {}

    def test_load_system_prompt(self, loader, config_dir):
        """システムプロンプトを読み込むテスト"""
        prompt_text = "これはテストプロンプトです。"

        # ファイル作成
        prompt_path = config_dir / "system_prompt.txt"
        with open(prompt_path, 'w', encoding='utf-8') as f:
            f.write(prompt_text)

        # 読み込み
        loaded_prompt = loader.load_system_prompt()

        assert loaded_prompt == prompt_text

    def test_load_system_prompt_not_found(self, loader):
        """プロンプトファイルが存在しない場合のテスト"""
        # デフォルトプロンプトが返される
        loaded_prompt = loader.load_system_prompt()
        assert isinstance(loaded_prompt, str)
        assert len(loaded_prompt) > 0

    def test_validate_config_success(self, loader, config_dir):
        """設定検証成功のテスト"""
        # APIキー作成
        api_keys = {"gemini": "test_key"}
        with open(config_dir / "api_keys.json", 'w') as f:
            json.dump(api_keys, f)

        # 価格設定作成
        pricing = {
            "test-model": {
                "input_token_price_per_1m": 2.0,
                "output_token_price_per_1m": 10.0
            }
        }
        with open(config_dir / "pricing.json", 'w') as f:
            json.dump(pricing, f)

        # 検証
        is_valid = loader.validate_config()
        assert is_valid is True

    def test_get_all_configs(self, loader, config_dir):
        """全設定取得のテスト"""
        # APIキー作成
        api_keys = {"gemini": "test_key"}
        with open(config_dir / "api_keys.json", 'w') as f:
            json.dump(api_keys, f)

        # 価格設定作成
        pricing = {"test-model": {"input_token_price_per_1m": 2.0, "output_token_price_per_1m": 10.0}}
        with open(config_dir / "pricing.json", 'w') as f:
            json.dump(pricing, f)

        # 全設定取得
        configs = loader.get_all_configs()

        assert 'api_keys' in configs
        assert 'pricing' in configs
        assert 'schema' in configs
        assert 'system_prompt' in configs

    def test_invalid_json(self, loader, config_dir):
        """無効なJSONファイルのテスト"""
        # 無効なJSON
        invalid_json_path = config_dir / "api_keys.json"
        with open(invalid_json_path, 'w') as f:
            f.write("{ invalid json }")

        # エラーが発生するはず
        with pytest.raises(ValueError):
            loader.load_api_keys()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
