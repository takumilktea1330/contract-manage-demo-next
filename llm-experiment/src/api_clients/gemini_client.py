"""
Gemini API クライアント

Google Gemini API を使用してPDFからデータを抽出するクライアント。
"""

import logging
from typing import Dict, Any, List
from pathlib import Path

from .base_client import BaseLLMClient

logger = logging.getLogger(__name__)


class GeminiClient(BaseLLMClient):
    """
    Gemini API クライアント

    Google Gemini Pro/Flash モデルを使用してPDFから構造化データを抽出します。
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.0-flash-exp",
        timeout: int = 60,
        max_retries: int = 3
    ):
        """
        Gemini クライアントの初期化

        Args:
            api_key: Google API キー
            model_name: 使用するモデル名（gemini-2.0-flash-exp, gemini-1.5-pro など）
            timeout: タイムアウト（秒）
            max_retries: 最大リトライ回数
        """
        super().__init__(api_key, model_name, timeout, max_retries)

        # TODO: Gemini SDK の初期化
        # import google.generativeai as genai
        # genai.configure(api_key=self.api_key)
        # self.model = genai.GenerativeModel(self.model_name)

        logger.info(f"GeminiClient 初期化: {model_name}")

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

            # TODO: プロンプトの構築
            # prompt = self._build_prompt(system_prompt, schema)

            # TODO: Gemini API の呼び出し（リトライ付き）
            # result, response_time = self._measure_time(
            #     self._retry_with_backoff,
            #     self._call_gemini_api,
            #     prompt,
            #     base64_images
            # )

            # TODO: レスポンスからJSONを抽出
            # extracted_json = self._extract_json_from_response(result.text)

            # TODO: トークン使用量の記録
            # self._last_input_tokens = result.usage_metadata.prompt_token_count
            # self._last_output_tokens = result.usage_metadata.candidates_token_count

            # TODO: 結果を返す
            # return {
            #     'extracted_data': extracted_json,
            #     'success': True,
            #     'error_message': None
            # }

            # 実装例のためのプレースホルダー
            raise NotImplementedError(
                "GeminiClient.extract_data_from_pdf() はまだ実装されていません。\n"
                "TODO コメントを参考に実装してください。"
            )

        except Exception as e:
            logger.error(f"Gemini API エラー: {str(e)}")
            return {
                'extracted_data': None,
                'success': False,
                'error_message': str(e)
            }

    def _build_prompt(self, system_prompt: str, schema: Dict) -> str:
        """
        APIに送信するプロンプトを構築する

        Args:
            system_prompt: システムプロンプト
            schema: JSONスキーマ

        Returns:
            構築されたプロンプト
        """
        # TODO: プロンプトの構築ロジックを実装
        # 例:
        # prompt = f"""{system_prompt}
        #
        # 以下のJSONスキーマに従ってデータを抽出してください:
        # {json.dumps(schema, ensure_ascii=False, indent=2)}
        #
        # 出力は以下の形式で返してください:
        # ```json
        # {{抽出されたデータ}}
        # ```
        # """
        # return prompt

        raise NotImplementedError("_build_prompt() を実装してください")

    def _call_gemini_api(self, prompt: str, images: List[str]) -> Any:
        """
        Gemini API を呼び出す

        Args:
            prompt: プロンプトテキスト
            images: Base64エンコードされた画像のリスト

        Returns:
            APIレスポンス
        """
        # TODO: Gemini API の実際の呼び出しを実装
        # 例:
        # import PIL.Image
        # import io
        # import base64
        #
        # # Base64画像をPIL Imageに変換
        # pil_images = []
        # for img_b64 in images:
        #     img_data = base64.b64decode(img_b64)
        #     pil_img = PIL.Image.open(io.BytesIO(img_data))
        #     pil_images.append(pil_img)
        #
        # # APIコール
        # response = self.model.generate_content(
        #     [prompt] + pil_images,
        #     generation_config={
        #         'temperature': 0.1,
        #         'max_output_tokens': 4096,
        #     }
        # )
        #
        # return response

        raise NotImplementedError("_call_gemini_api() を実装してください")
