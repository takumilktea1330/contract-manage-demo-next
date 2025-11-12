"""
OpenAI GPT API クライアント

OpenAI GPT-4o API を使用してPDFからデータを抽出するクライアント。
"""

import logging
from typing import Dict, Any, List
from pathlib import Path

from .base_client import BaseLLMClient

logger = logging.getLogger(__name__)


class GPTClient(BaseLLMClient):
    """
    OpenAI GPT API クライアント

    GPT-4o モデルを使用してPDFから構造化データを抽出します。
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "gpt-4o",
        timeout: int = 60,
        max_retries: int = 3
    ):
        """
        GPT クライアントの初期化

        Args:
            api_key: OpenAI API キー
            model_name: 使用するモデル名（gpt-4o, gpt-4o-mini など）
            timeout: タイムアウト（秒）
            max_retries: 最大リトライ回数
        """
        super().__init__(api_key, model_name, timeout, max_retries)

        # TODO: OpenAI SDK の初期化
        # from openai import OpenAI
        # self.client = OpenAI(api_key=self.api_key, timeout=self.timeout)

        logger.info(f"GPTClient 初期化: {model_name}")

    def extract_data_from_pdf(
        self,
        pdf_path: str,
        system_prompt: str,
        schema: Dict
    ) -> Dict[str, Any]:
        """
        PDFからデータを抽出する

        Args:
            pdf_path: PDFファイルのパス
            system_prompt: システムプロンプト
            schema: JSONスキーマ

        Returns:
            抽出結果の辞書:
            {
                'extracted_data': Dict,  # 抽出されたJSON
                'success': bool,         # 成功したか
                'error_message': str     # エラーメッセージ（失敗時）
            }
        """
        # APIキーの検証
        if not self._validate_api_key():
            return {
                'extracted_data': None,
                'success': False,
                'error_message': 'APIキーが無効です'
            }

        try:
            # TODO: PDFを画像に変換
            # from src.processors import ImageConverter
            # converter = ImageConverter()
            # base64_images = converter.pdf_to_base64_images(pdf_path)

            # TODO: メッセージの構築
            # messages = self._build_messages(system_prompt, schema, base64_images)

            # TODO: OpenAI API の呼び出し（リトライ付き）
            # response, response_time = self._measure_time(
            #     self._retry_with_backoff,
            #     self._call_openai_api,
            #     messages
            # )

            # TODO: レスポンスからJSONを抽出
            # response_text = response.choices[0].message.content
            # extracted_json = self._extract_json_from_response(response_text)

            # TODO: トークン使用量の記録
            # self._last_input_tokens = response.usage.prompt_tokens
            # self._last_output_tokens = response.usage.completion_tokens

            # TODO: 結果を返す
            # return {
            #     'extracted_data': extracted_json,
            #     'success': True,
            #     'error_message': None
            # }

            # 実装例のためのプレースホルダー
            raise NotImplementedError(
                "GPTClient.extract_data_from_pdf() はまだ実装されていません。\n"
                "TODO コメントを参考に実装してください。"
            )

        except Exception as e:
            logger.error(f"OpenAI API エラー: {str(e)}")
            return {
                'extracted_data': None,
                'success': False,
                'error_message': str(e)
            }

    def _build_messages(
        self,
        system_prompt: str,
        schema: Dict,
        images: List[str]
    ) -> List[Dict]:
        """
        APIに送信するメッセージを構築する

        Args:
            system_prompt: システムプロンプト
            schema: JSONスキーマ
            images: Base64エンコードされた画像のリスト

        Returns:
            メッセージのリスト
        """
        # TODO: メッセージの構築ロジックを実装
        # 例:
        # import json
        #
        # messages = [
        #     {
        #         "role": "system",
        #         "content": system_prompt
        #     },
        #     {
        #         "role": "user",
        #         "content": [
        #             {
        #                 "type": "text",
        #                 "text": f"以下のJSONスキーマに従ってデータを抽出してください:\n"
        #                         f"{json.dumps(schema, ensure_ascii=False, indent=2)}"
        #             }
        #         ]
        #     }
        # ]
        #
        # # 画像を追加
        # for img_b64 in images:
        #     messages[1]["content"].append({
        #         "type": "image_url",
        #         "image_url": {
        #             "url": f"data:image/jpeg;base64,{img_b64}"
        #         }
        #     })
        #
        # return messages

        raise NotImplementedError("_build_messages() を実装してください")

    def _call_openai_api(self, messages: List[Dict]) -> Any:
        """
        OpenAI API を呼び出す

        Args:
            messages: メッセージリスト

        Returns:
            APIレスポンス
        """
        # TODO: OpenAI API の実際の呼び出しを実装
        # 例:
        # response = self.client.chat.completions.create(
        #     model=self.model_name,
        #     messages=messages,
        #     temperature=0.1,
        #     max_tokens=4096,
        #     response_format={"type": "json_object"}  # JSON モード（オプション）
        # )
        #
        # return response

        raise NotImplementedError("_call_openai_api() を実装してください")
