"""
LLMクライアントの基底クラス

すべてのLLMクライアントが継承する基底クラス。
共通機能（リトライ、タイムアウト、レスポンスタイム計測など）を提供する。
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    """
    LLMクライアントの基底クラス

    すべてのLLMクライアントはこのクラスを継承し、
    extract_data_from_pdfメソッドを実装する必要があります。
    """

    def __init__(
        self,
        api_key: str,
        model_name: str,
        timeout: int = 60,
        max_retries: int = 3
    ):
        """
        基底クライアントの初期化

        Args:
            api_key: APIキー
            model_name: モデル名
            timeout: タイムアウト（秒）
            max_retries: 最大リトライ回数
        """
        self.api_key = api_key
        self.model_name = model_name
        self.timeout = timeout
        self.max_retries = max_retries

        # レスポンス情報
        self._last_response_time: Optional[float] = None
        self._last_input_tokens: Optional[int] = None
        self._last_output_tokens: Optional[int] = None

        logger.info(f"{self.__class__.__name__} 初期化完了: model={model_name}")

    @abstractmethod
    def extract_data_from_pdf(
        self,
        pdf_path: str,
        system_prompt: str,
        schema: Dict
    ) -> Dict[str, Any]:
        """
        PDFからデータを抽出する（各クライアントで実装）

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
        pass

    def get_response_time(self) -> Optional[float]:
        """
        最後のリクエストのレスポンスタイムを取得

        Returns:
            レスポンスタイム（秒）
        """
        return self._last_response_time

    def get_token_usage(self) -> Dict[str, int]:
        """
        最後のリクエストのトークン使用量を取得

        Returns:
            トークン使用量の辞書
        """
        return {
            'input_tokens': self._last_input_tokens or 0,
            'output_tokens': self._last_output_tokens or 0
        }

    def _retry_with_backoff(
        self,
        func,
        *args,
        **kwargs
    ) -> Any:
        """
        指数バックオフでリトライを行う

        Args:
            func: 実行する関数
            *args: 関数の引数
            **kwargs: 関数のキーワード引数

        Returns:
            関数の実行結果

        Raises:
            最後に発生した例外
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)

            except Exception as e:
                last_exception = e
                wait_time = 2 ** attempt  # 指数バックオフ: 1, 2, 4秒

                if attempt < self.max_retries - 1:
                    logger.warning(
                        f"リトライ {attempt + 1}/{self.max_retries}: "
                        f"{str(e)} ({wait_time}秒後に再試行)"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"最大リトライ回数に達しました: {str(e)}")

        raise last_exception

    def _measure_time(self, func, *args, **kwargs) -> tuple:
        """
        関数の実行時間を計測する

        Args:
            func: 実行する関数
            *args: 関数の引数
            **kwargs: 関数のキーワード引数

        Returns:
            (実行結果, 実行時間)
        """
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time

        self._last_response_time = elapsed_time
        return result, elapsed_time

    def _extract_json_from_response(self, response_text: str) -> Optional[Dict]:
        """
        レスポンステキストからJSONを抽出する

        Args:
            response_text: レスポンステキスト

        Returns:
            抽出されたJSON（失敗時はNone）
        """
        import json
        import re

        # JSONブロックを探す（```json ... ``` 形式）
        json_match = re.search(r'```json\s*\n(.*?)\n```', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # 直接JSONとしてパースを試みる
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass

        # { } で囲まれた部分を探す
        brace_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass

        logger.warning("レスポンスからJSONを抽出できませんでした")
        return None

    def _validate_api_key(self) -> bool:
        """
        APIキーが有効かチェックする

        Returns:
            有効な場合True
        """
        if not self.api_key or self.api_key.startswith('YOUR_'):
            logger.error("APIキーが設定されていません")
            return False
        return True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model_name})"
