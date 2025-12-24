"""
APIクライアントのテストテンプレート

このファイルをコピーして test_<client_name>.py を作成してください。
例: test_gpt_client.py, test_gemini_client.py
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch

# TODO: 適切なクライアントをインポート
# from src.api_clients import GPTClient, GeminiClient, ClaudeClient, AzureDocumentClient


class TestAPIClient:
    """APIクライアントのテストクラス"""

    @pytest.fixture
    def api_key(self):
        """
        APIキーをロード

        config/api_keys.json または環境変数から読み込みます。
        """
        # TODO: 適切なキー名に変更
        key_name = "openai"  # "anthropic", "gemini", "azure" など

        # 設定ファイルから読み込み
        config_path = Path(__file__).parent.parent / "config" / "api_keys.json"
        if config_path.exists():
            with open(config_path) as f:
                keys = json.load(f)
                if keys.get(key_name):
                    return keys[key_name]

        # 環境変数から読み込み
        import os
        env_key = os.getenv(f"{key_name.upper()}_API_KEY")
        if env_key:
            return env_key

        pytest.skip(f"{key_name} APIキーが設定されていません")

    @pytest.fixture
    def client(self, api_key):
        """
        クライアントのインスタンスを作成

        TODO: 適切なクライアントクラスに変更
        """
        # 例: return GPTClient(api_key=api_key, model_name="gpt-4o")
        pytest.skip("クライアントの初期化を実装してください")

    @pytest.fixture
    def test_pdf_path(self):
        """テスト用PDFのパスを取得"""
        pdf_path = Path(__file__).parent.parent / "data" / "input" / "sample_contract.pdf"

        if not pdf_path.exists():
            pytest.skip("テスト用PDFが存在しません")

        return str(pdf_path)

    @pytest.fixture
    def schema(self):
        """JSONスキーマを読み込む"""
        schema_path = Path(__file__).parent.parent / "config" / "schema.json"

        if not schema_path.exists():
            pytest.skip("スキーマファイルが存在しません")

        with open(schema_path) as f:
            return json.load(f)

    @pytest.fixture
    def system_prompt(self):
        """システムプロンプトを取得"""
        return "不動産賃貸借契約書から情報を抽出してください。"

    # ========================================
    # 基本機能のテスト
    # ========================================

    def test_client_initialization(self, client):
        """クライアントが正しく初期化されることを確認"""
        assert client is not None
        assert client.api_key is not None
        assert client.model_name is not None
        assert client.timeout > 0
        assert client.max_retries > 0

    def test_extract_data_from_pdf(self, client, test_pdf_path, system_prompt, schema):
        """
        PDFからデータを抽出するテスト

        実際のAPI呼び出しを行うため、APIキーが必要です。
        """
        result = client.extract_data_from_pdf(
            pdf_path=test_pdf_path,
            system_prompt=system_prompt,
            schema=schema
        )

        # 成功したか確認
        assert result['success'] == True, f"エラー: {result.get('error_message')}"
        assert result['extracted_data'] is not None
        assert isinstance(result['extracted_data'], dict)

        # 抽出データの基本構造を確認
        assert 'metadata' in result['extracted_data'] or 'content' in result['extracted_data']

    def test_response_time_tracking(self, client, test_pdf_path, system_prompt, schema):
        """レスポンスタイムが記録されることを確認"""
        client.extract_data_from_pdf(
            pdf_path=test_pdf_path,
            system_prompt=system_prompt,
            schema=schema
        )

        response_time = client.get_response_time()
        assert response_time is not None
        assert response_time > 0

    def test_token_usage_tracking(self, client, test_pdf_path, system_prompt, schema):
        """トークン使用量が記録されることを確認"""
        result = client.extract_data_from_pdf(
            pdf_path=test_pdf_path,
            system_prompt=system_prompt,
            schema=schema
        )

        if result['success']:
            tokens = client.get_token_usage()
            assert tokens['input_tokens'] > 0
            assert tokens['output_tokens'] > 0

    # ========================================
    # エラーハンドリングのテスト
    # ========================================

    def test_invalid_api_key(self):
        """無効なAPIキーで失敗することを確認"""
        # TODO: 適切なクライアントクラスに変更
        # client = GPTClient(api_key="invalid_key")
        pytest.skip("無効なAPIキーのテストを実装してください")

        result = client.extract_data_from_pdf(
            pdf_path="data/input/sample_contract.pdf",
            system_prompt="test",
            schema={}
        )

        assert result['success'] == False
        assert result['error_message'] is not None

    def test_nonexistent_pdf(self, client, system_prompt, schema):
        """存在しないPDFで失敗することを確認"""
        result = client.extract_data_from_pdf(
            pdf_path="nonexistent.pdf",
            system_prompt=system_prompt,
            schema=schema
        )

        assert result['success'] == False
        assert result['error_message'] is not None

    # ========================================
    # モックを使ったユニットテスト
    # ========================================

    def test_extract_json_from_response(self, client):
        """レスポンスからJSON抽出が正しく動作することを確認"""
        # JSONコードブロック形式
        response_text = """
        以下がJSONです:
        ```json
        {
            "contract_type": "普通賃貸借契約",
            "rent": 100000
        }
        ```
        """

        extracted = client._extract_json_from_response(response_text)
        assert extracted is not None
        assert extracted['contract_type'] == "普通賃貸借契約"
        assert extracted['rent'] == 100000

        # 直接JSON形式
        response_text2 = '{"contract_type": "定期借家契約", "deposit": 200000}'
        extracted2 = client._extract_json_from_response(response_text2)
        assert extracted2 is not None
        assert extracted2['contract_type'] == "定期借家契約"

    def test_validate_api_key(self, client):
        """APIキー検証が正しく動作することを確認"""
        # 有効なAPIキー
        assert client._validate_api_key() == True

        # 無効なAPIキー
        client.api_key = None
        assert client._validate_api_key() == False

        client.api_key = "YOUR_API_KEY"
        assert client._validate_api_key() == False

    @patch('time.sleep')  # sleepをモック化してテストを高速化
    def test_retry_logic(self, mock_sleep, client):
        """リトライロジックが正しく動作することを確認"""
        call_count = 0

        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("一時的なエラー")
            return "成功"

        # リトライで成功する
        result = client._retry_with_backoff(failing_function)
        assert result == "成功"
        assert call_count == 3
        assert mock_sleep.call_count == 2  # 2回リトライ（1秒、2秒）

    @patch('time.sleep')
    def test_retry_exhaustion(self, mock_sleep, client):
        """最大リトライ回数に達したら例外が発生することを確認"""
        def always_failing_function():
            raise Exception("常に失敗")

        with pytest.raises(Exception, match="常に失敗"):
            client._retry_with_backoff(always_failing_function)

        # max_retries = 3 なので、3回呼び出される
        assert mock_sleep.call_count == client.max_retries - 1

    # ========================================
    # パフォーマンステスト（オプション）
    # ========================================

    @pytest.mark.slow
    def test_large_pdf_processing(self, client, system_prompt, schema):
        """
        大きなPDFの処理をテスト

        @pytest.mark.slow を使用して通常のテストではスキップ
        pytest -v -m slow で実行
        """
        large_pdf_path = "data/input/large_contract.pdf"

        if not Path(large_pdf_path).exists():
            pytest.skip("大きなテスト用PDFが存在しません")

        result = client.extract_data_from_pdf(
            pdf_path=large_pdf_path,
            system_prompt=system_prompt,
            schema=schema
        )

        assert result['success'] == True

        # レスポンスタイムを確認（警告のみ）
        response_time = client.get_response_time()
        if response_time > 30:
            print(f"⚠️ 警告: レスポンスタイムが長い ({response_time:.2f}秒)")

    # ========================================
    # 統合テスト（オプション）
    # ========================================

    @pytest.mark.integration
    def test_full_workflow_integration(self, client, test_pdf_path, system_prompt, schema):
        """
        完全なワークフローの統合テスト

        1. PDF抽出
        2. スキーマ検証
        3. 精度計算

        @pytest.mark.integration を使用して通常のテストではスキップ
        pytest -v -m integration で実行
        """
        from src.evaluators import SchemaValidator, AccuracyCalculator

        # 1. データ抽出
        result = client.extract_data_from_pdf(
            pdf_path=test_pdf_path,
            system_prompt=system_prompt,
            schema=schema
        )

        assert result['success'] == True
        extracted_data = result['extracted_data']

        # 2. スキーマ検証
        validator = SchemaValidator(schema)
        is_valid, errors = validator.validate(extracted_data)

        if not is_valid:
            print(f"⚠️ スキーマ検証エラー: {errors}")

        # 3. 精度計算（正解データがあれば）
        golden_path = Path(test_pdf_path).stem + ".json"
        golden_file = Path(__file__).parent.parent / "data" / "golden" / golden_path

        if golden_file.exists():
            with open(golden_file) as f:
                golden_data = json.load(f)

            accuracy_calc = AccuracyCalculator(golden_data, extracted_data)
            metrics = accuracy_calc.get_metrics()

            print(f"📊 精度メトリクス:")
            print(f"  - Field Accuracy: {metrics['field_accuracy']:.2%}")
            print(f"  - F1 Score: {metrics['f1_score']:.2%}")
            print(f"  - Exact Match: {metrics['exact_match']}")


# ========================================
# テスト実行例
# ========================================
"""
基本テスト:
pytest tests/test_<client_name>.py -v

スローテストも含める:
pytest tests/test_<client_name>.py -v -m slow

統合テストも含める:
pytest tests/test_<client_name>.py -v -m integration

カバレッジ付き:
pytest tests/test_<client_name>.py --cov=src.api_clients.<client_name> --cov-report=html
"""
