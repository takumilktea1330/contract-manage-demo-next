# API連携モジュール実装ガイド

## 概要

このガイドでは、各LLM APIクライアントの実装方法について説明します。
すべてのAPIクライアントは `BaseLLMClient` 抽象基底クラスを継承し、共通のインターフェースを実装します。

## 目次

1. [アーキテクチャ](#アーキテクチャ)
2. [BaseLLMClient の機能](#basellmclient-の機能)
3. [実装手順](#実装手順)
4. [各クライアントの実装ポイント](#各クライアントの実装ポイント)
5. [テスト方法](#テスト方法)
6. [トラブルシューティング](#トラブルシューティング)

---

## アーキテクチャ

### クラス図

```
BaseLLMClient (抽象基底クラス)
    ├── GeminiClient
    ├── GPTClient
    ├── ClaudeClient
    └── AzureDocumentClient
```

### 共通機能（BaseLLMClient が提供）

- ✅ リトライロジック（指数バックオフ）
- ✅ タイムアウト管理
- ✅ レスポンスタイム計測
- ✅ トークン使用量の記録
- ✅ JSONレスポンスの抽出
- ✅ APIキーの検証
- ✅ エラーハンドリング

### 各クライアントが実装する機能

- ❌ API固有の初期化（SDK のセットアップ）
- ❌ `extract_data_from_pdf()` メソッド
- ❌ プロンプト/メッセージの構築
- ❌ API呼び出しの実装

---

## BaseLLMClient の機能

### コンストラクタ

```python
def __init__(
    self,
    api_key: str,
    model_name: str,
    timeout: int = 60,
    max_retries: int = 3
)
```

**パラメータ:**
- `api_key`: APIキー
- `model_name`: モデル名
- `timeout`: タイムアウト（秒）
- `max_retries`: 最大リトライ回数

### 抽象メソッド

#### `extract_data_from_pdf()`

**必須実装メソッド** - すべてのサブクラスで実装が必要です。

```python
@abstractmethod
def extract_data_from_pdf(
    self,
    pdf_path: str,
    system_prompt: str,
    schema: Dict
) -> Dict[str, Any]:
    """
    PDFからデータを抽出する

    Returns:
        {
            'extracted_data': Dict,  # 抽出されたJSON
            'success': bool,         # 成功したか
            'error_message': str     # エラーメッセージ（失敗時）
        }
    """
    pass
```

### ヘルパーメソッド

#### `_retry_with_backoff(func, *args, **kwargs)`

指数バックオフでリトライを実行します。

```python
result = self._retry_with_backoff(
    self._call_api,
    arg1,
    arg2
)
```

#### `_measure_time(func, *args, **kwargs)`

関数の実行時間を計測し、`self._last_response_time` に記録します。

```python
result, elapsed_time = self._measure_time(
    self._call_api,
    arg1,
    arg2
)
```

#### `_extract_json_from_response(response_text: str)`

レスポンステキストからJSONを抽出します。以下の形式に対応：
- ````json ... ``` ` 形式のコードブロック
- 直接のJSON文字列
- `{ }` で囲まれた部分

```python
json_data = self._extract_json_from_response(response_text)
```

#### `_validate_api_key()`

APIキーが有効かチェックします。

```python
if not self._validate_api_key():
    return {'success': False, 'error_message': 'APIキーが無効です'}
```

### プロパティ

#### `get_response_time()`

最後のリクエストのレスポンスタイムを取得します。

```python
response_time = client.get_response_time()
```

#### `get_token_usage()`

最後のリクエストのトークン使用量を取得します。

```python
tokens = client.get_token_usage()
# {'input_tokens': 1234, 'output_tokens': 567}
```

---

## 実装手順

### ステップ1: テンプレートファイルを確認

以下のテンプレートファイルがすでに用意されています：

- `src/api_clients/gemini_client.py`
- `src/api_clients/gpt_client.py`
- `src/api_clients/claude_client.py`
- `src/api_clients/azure_client.py`

各ファイルには `TODO` コメントが記載されており、実装が必要な箇所が明示されています。

### ステップ2: 必要なライブラリをインストール

#### Gemini

```bash
pip install google-generativeai
```

#### GPT

```bash
pip install openai
```

#### Claude

```bash
pip install anthropic
```

#### Azure Document Intelligence

```bash
pip install azure-ai-formrecognizer
```

### ステップ3: SDKの初期化を実装

`__init__()` メソッド内でSDKを初期化します。

**例（GPT）:**

```python
from openai import OpenAI

def __init__(self, api_key: str, model_name: str = "gpt-4o", ...):
    super().__init__(api_key, model_name, timeout, max_retries)

    # SDK の初期化
    self.client = OpenAI(api_key=self.api_key, timeout=self.timeout)

    logger.info(f"GPTClient 初期化: {model_name}")
```

### ステップ4: `extract_data_from_pdf()` を実装

このメソッドがメインの処理フローです。

**推奨実装パターン:**

```python
def extract_data_from_pdf(self, pdf_path: str, system_prompt: str, schema: Dict) -> Dict[str, Any]:
    # 1. APIキーの検証
    if not self._validate_api_key():
        return {'extracted_data': None, 'success': False, 'error_message': 'APIキーが無効です'}

    try:
        # 2. PDFを画像に変換
        from src.processors import ImageConverter
        converter = ImageConverter()
        base64_images = converter.pdf_to_base64_images(pdf_path)

        # 3. プロンプト/メッセージを構築
        messages = self._build_messages(system_prompt, schema, base64_images)

        # 4. API呼び出し（リトライ + 時間計測）
        response, response_time = self._measure_time(
            self._retry_with_backoff,
            self._call_api,
            messages
        )

        # 5. レスポンスからJSONを抽出
        response_text = self._get_response_text(response)
        extracted_json = self._extract_json_from_response(response_text)

        # 6. トークン使用量を記録
        self._last_input_tokens = self._get_input_tokens(response)
        self._last_output_tokens = self._get_output_tokens(response)

        # 7. 結果を返す
        return {
            'extracted_data': extracted_json,
            'success': True,
            'error_message': None
        }

    except Exception as e:
        logger.error(f"API エラー: {str(e)}")
        return {'extracted_data': None, 'success': False, 'error_message': str(e)}
```

### ステップ5: ヘルパーメソッドを実装

#### プロンプト/メッセージ構築

各APIのメッセージ形式に合わせて構築します。

#### API呼び出し

実際のAPIコールを行います。`_retry_with_backoff()` と組み合わせて使用してください。

### ステップ6: テストを実装

`tests/test_<client_name>.py` にテストを作成します。

---

## 各クライアントの実装ポイント

### Gemini Client

#### 特徴
- Google の `google-generativeai` SDKを使用
- PIL Image オブジェクトでマルチモーダル入力

#### 実装例

```python
import google.generativeai as genai
import PIL.Image
import io
import base64

def __init__(self, api_key, model_name="gemini-2.0-flash-exp", ...):
    super().__init__(api_key, model_name, timeout, max_retries)
    genai.configure(api_key=self.api_key)
    self.model = genai.GenerativeModel(self.model_name)

def _call_gemini_api(self, prompt: str, images: List[str]):
    # Base64画像をPIL Imageに変換
    pil_images = []
    for img_b64 in images:
        img_data = base64.b64decode(img_b64)
        pil_img = PIL.Image.open(io.BytesIO(img_data))
        pil_images.append(pil_img)

    # APIコール
    response = self.model.generate_content(
        [prompt] + pil_images,
        generation_config={
            'temperature': 0.1,
            'max_output_tokens': 4096,
        }
    )

    return response
```

#### トークン取得

```python
self._last_input_tokens = response.usage_metadata.prompt_token_count
self._last_output_tokens = response.usage_metadata.candidates_token_count
```

---

### GPT Client

#### 特徴
- OpenAI の `openai` SDKを使用
- メッセージベースのAPI
- `response_format={"type": "json_object"}` でJSON出力を強制可能

#### 実装例

```python
from openai import OpenAI

def __init__(self, api_key, model_name="gpt-4o", ...):
    super().__init__(api_key, model_name, timeout, max_retries)
    self.client = OpenAI(api_key=self.api_key, timeout=self.timeout)

def _build_messages(self, system_prompt: str, schema: Dict, images: List[str]):
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"JSONスキーマ:\n{json.dumps(schema, ensure_ascii=False, indent=2)}"
                }
            ]
        }
    ]

    # 画像を追加
    for img_b64 in images:
        messages[1]["content"].append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
        })

    return messages

def _call_openai_api(self, messages: List[Dict]):
    response = self.client.chat.completions.create(
        model=self.model_name,
        messages=messages,
        temperature=0.1,
        max_tokens=4096,
        response_format={"type": "json_object"}  # JSON モード
    )
    return response
```

#### トークン取得

```python
self._last_input_tokens = response.usage.prompt_tokens
self._last_output_tokens = response.usage.completion_tokens
```

---

### Claude Client

#### 特徴
- Anthropic の `anthropic` SDKを使用
- システムプロンプトは別パラメータ
- Base64画像をメッセージに埋め込む

#### 実装例

```python
from anthropic import Anthropic

def __init__(self, api_key, model_name="claude-3-5-sonnet-20241022", ...):
    super().__init__(api_key, model_name, timeout, max_retries)
    self.client = Anthropic(api_key=self.api_key, timeout=self.timeout)

def _build_messages(self, schema: Dict, images: List[str]):
    content = [
        {
            "type": "text",
            "text": f"JSONスキーマ:\n{json.dumps(schema, ensure_ascii=False, indent=2)}"
        }
    ]

    # 画像を追加
    for img_b64 in images:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": img_b64
            }
        })

    return [{"role": "user", "content": content}]

def _call_claude_api(self, system_prompt: str, messages: List[Dict]):
    response = self.client.messages.create(
        model=self.model_name,
        max_tokens=4096,
        temperature=0.1,
        system=system_prompt,
        messages=messages
    )
    return response
```

#### トークン取得

```python
self._last_input_tokens = response.usage.input_tokens
self._last_output_tokens = response.usage.output_tokens
```

---

### Azure Document Intelligence Client

#### 特徴
- Microsoft の `azure-ai-formrecognizer` SDKを使用
- 専用のドキュメント分析サービス
- LLMではないため、結果を手動でスキーマに変換する必要がある

#### 実装例

```python
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

def __init__(self, api_key, endpoint, model_name="prebuilt-document", ...):
    super().__init__(api_key, model_name, timeout, max_retries)
    self.endpoint = endpoint
    self.client = DocumentAnalysisClient(
        endpoint=self.endpoint,
        credential=AzureKeyCredential(self.api_key)
    )

def _call_azure_api(self, pdf_data: bytes):
    poller = self.client.begin_analyze_document(
        model_id=self.model_name,
        document=pdf_data
    )
    result = poller.result()
    return result

def _transform_to_schema(self, azure_result, schema: Dict):
    # Azure の結果を目標スキーマに変換
    extracted_data = {
        "metadata": {
            "title": self._extract_field(azure_result, "title"),
            "number_page": len(azure_result.pages),
            "language": "ja"
        },
        "content": {
            # ... フィールドをマッピング
        }
    }
    return extracted_data
```

#### トークン推定

Azure は明示的なトークン数を返さないため、ページ数やテキスト量から推定します。

```python
from src.processors import PDFProcessor

processor = PDFProcessor()
page_count = processor.get_page_count(pdf_path)
self._last_input_tokens = page_count * 1000  # 1ページあたり1000トークンと仮定
self._last_output_tokens = len(str(extracted_json)) // 4  # 文字数の1/4と仮定
```

---

## テスト方法

### ユニットテストの作成

`tests/test_<client_name>.py` を作成します。

```python
import pytest
import json
from pathlib import Path
from src.api_clients import GPTClient

@pytest.fixture
def api_key():
    """APIキーをロード"""
    config_path = Path(__file__).parent.parent / "config" / "api_keys.json"
    if not config_path.exists():
        pytest.skip("APIキーが設定されていません")

    with open(config_path) as f:
        keys = json.load(f)

    if not keys.get('openai'):
        pytest.skip("OpenAI APIキーが設定されていません")

    return keys['openai']

@pytest.fixture
def gpt_client(api_key):
    """GPTクライアントのインスタンスを作成"""
    return GPTClient(api_key=api_key, model_name="gpt-4o")

def test_extract_data_from_pdf(gpt_client):
    """PDFからデータを抽出するテスト"""
    pdf_path = "data/input/sample_contract.pdf"

    if not Path(pdf_path).exists():
        pytest.skip("テスト用PDFが存在しません")

    # システムプロンプトとスキーマを読み込む
    with open("config/schema.json") as f:
        schema = json.load(f)

    system_prompt = "不動産賃貸借契約書から情報を抽出してください。"

    # データ抽出を実行
    result = gpt_client.extract_data_from_pdf(
        pdf_path=pdf_path,
        system_prompt=system_prompt,
        schema=schema
    )

    # アサーション
    assert result['success'] == True
    assert result['extracted_data'] is not None
    assert isinstance(result['extracted_data'], dict)

    # レスポンスタイムとトークン使用量が記録されているか
    assert gpt_client.get_response_time() > 0
    tokens = gpt_client.get_token_usage()
    assert tokens['input_tokens'] > 0
    assert tokens['output_tokens'] > 0

def test_invalid_api_key():
    """無効なAPIキーのテスト"""
    client = GPTClient(api_key="invalid_key")

    result = client.extract_data_from_pdf(
        pdf_path="data/input/sample_contract.pdf",
        system_prompt="test",
        schema={}
    )

    assert result['success'] == False
```

### テストの実行

```bash
# 特定のクライアントのテストを実行
pytest tests/test_gpt_client.py -v

# すべてのAPIクライアントテストを実行
pytest tests/test_*_client.py -v

# カバレッジ付き
pytest tests/test_gpt_client.py --cov=src.api_clients.gpt_client --cov-report=html
```

### 手動テスト

実装が完了したら、メインスクリプトで実際に動作確認します。

```bash
# 特定のモデルを指定して実行
python src/main.py --models gpt-4o --pdf sample_contract.pdf

# 複数モデルで実行
python src/main.py --models gpt-4o claude-3-5-sonnet-20241022 gemini-2.0-flash-exp
```

---

## トラブルシューティング

### APIキーエラー

**エラー:** `APIキーが無効です`

**解決方法:**
1. `config/api_keys.json` にAPIキーが正しく設定されているか確認
2. 環境変数 `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` などが設定されているか確認
3. APIキーが有効期限切れでないか確認

### タイムアウトエラー

**エラー:** `Timeout error`

**解決方法:**
1. `timeout` パラメータを増やす（デフォルト60秒）
2. PDFのページ数が多い場合は、DPIを下げて画像サイズを小さくする
3. ネットワーク接続を確認

### レート制限エラー

**エラー:** `Rate limit exceeded`

**解決方法:**
1. `max_retries` を増やす（デフォルト3回）
2. リトライ間隔が自動的に増加します（指数バックオフ: 1秒、2秒、4秒）
3. API のレート制限を確認し、必要に応じて有料プランにアップグレード

### JSON抽出エラー

**エラー:** `レスポンスからJSONを抽出できませんでした`

**解決方法:**
1. プロンプトでJSON形式での出力を明示的に指示
2. GPTの場合は `response_format={"type": "json_object"}` を使用
3. レスポンステキストをログ出力して内容を確認
4. 必要に応じて `_extract_json_from_response()` をカスタマイズ

### トークン数が記録されない

**解決方法:**
1. 各APIのレスポンス構造を確認
2. `_last_input_tokens` と `_last_output_tokens` が正しく設定されているか確認
3. APIによってはトークン数が含まれない場合があるため、ドキュメントを参照

---

## まとめ

### 実装チェックリスト

- [ ] 必要なライブラリをインストール
- [ ] SDK の初期化を実装（`__init__`）
- [ ] `extract_data_from_pdf()` メソッドを実装
- [ ] プロンプト/メッセージ構築メソッドを実装
- [ ] API呼び出しメソッドを実装
- [ ] トークン使用量の記録を実装
- [ ] エラーハンドリングを実装
- [ ] ユニットテストを作成
- [ ] 手動テストで動作確認
- [ ] ドキュメントを更新

### 実装後の統合

すべてのクライアントが実装されたら、以下のコマンドで全モデルを比較できます:

```bash
python src/main.py --models \
    gpt-4o \
    claude-3-5-sonnet-20241022 \
    gemini-2.0-flash-exp \
    azure-document-intelligence
```

実験結果は `output/` ディレクトリに保存され、自動的に可視化グラフが生成されます。

---

## 参考資料

- [Gemini API ドキュメント](https://ai.google.dev/docs)
- [OpenAI API ドキュメント](https://platform.openai.com/docs)
- [Anthropic API ドキュメント](https://docs.anthropic.com/)
- [Azure Document Intelligence ドキュメント](https://learn.microsoft.com/azure/ai-services/document-intelligence/)

---

質問や問題がある場合は、プロジェクトのIssueを作成してください。
