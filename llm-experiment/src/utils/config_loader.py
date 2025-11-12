"""
設定読み込みモジュール

実験に必要な設定ファイル（APIキー、価格設定、スキーマ、プロンプト）を読み込む。
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Any
from dotenv import load_dotenv


logger = logging.getLogger(__name__)


class ConfigLoader:
    """設定ファイルを読み込むクラス"""

    def __init__(self, config_dir: str = "config"):
        """
        ConfigLoaderの初期化

        Args:
            config_dir: 設定ファイルのディレクトリ
        """
        self.config_dir = Path(config_dir)

        if not self.config_dir.exists():
            logger.warning(f"設定ディレクトリが存在しません: {self.config_dir}")
            self.config_dir.mkdir(parents=True, exist_ok=True)

        # 環境変数を読み込む
        load_dotenv()

        logger.info(f"ConfigLoader初期化完了: {self.config_dir}")

    def load_api_keys(self, file_name: str = "api_keys.json") -> Dict[str, Any]:
        """
        APIキーを読み込む

        Args:
            file_name: APIキーファイル名

        Returns:
            APIキーの辞書

        Raises:
            FileNotFoundError: ファイルが存在しない場合
            ValueError: JSONが無効な場合
        """
        file_path = self.config_dir / file_name

        # ファイルが存在しない場合は環境変数から取得を試みる
        if not file_path.exists():
            logger.warning(f"APIキーファイルが見つかりません: {file_path}")
            logger.info("環境変数からAPIキーを取得します")

            api_keys = {
                'gemini': os.getenv('GEMINI_API_KEY'),
                'openai': os.getenv('OPENAI_API_KEY'),
                'anthropic': os.getenv('ANTHROPIC_API_KEY'),
                'azure': {
                    'endpoint': os.getenv('AZURE_ENDPOINT'),
                    'key': os.getenv('AZURE_KEY')
                }
            }

            # 空の値を除外
            api_keys = {k: v for k, v in api_keys.items() if v is not None}

            if not api_keys:
                raise FileNotFoundError(
                    f"APIキーファイルが見つからず、環境変数も設定されていません。\n"
                    f"以下のいずれかを実行してください:\n"
                    f"1. {file_path} を作成\n"
                    f"2. 環境変数を設定（GEMINI_API_KEY, OPENAI_API_KEY等）"
                )

            logger.info(f"環境変数からAPIキーを取得しました: {list(api_keys.keys())}")
            return api_keys

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                api_keys = json.load(f)

            # キーが設定されているか確認
            valid_keys = {k: v for k, v in api_keys.items()
                         if v and not str(v).startswith('YOUR_')}

            if not valid_keys:
                logger.warning("APIキーが設定されていません（YOUR_*のまま）")

            logger.info(f"APIキーを読み込みました: {file_path} ({len(valid_keys)}個)")
            return api_keys

        except json.JSONDecodeError as e:
            logger.error(f"APIキーファイルのJSONパースに失敗: {str(e)}")
            raise ValueError(f"APIキーファイルのJSONが無効です: {str(e)}")
        except Exception as e:
            logger.error(f"APIキーの読み込みに失敗: {str(e)}")
            raise

    def load_pricing(self, file_name: str = "pricing.json") -> Dict[str, Dict]:
        """
        価格設定を読み込む

        Args:
            file_name: 価格設定ファイル名

        Returns:
            価格設定の辞書

        Raises:
            FileNotFoundError: ファイルが存在しない場合
            ValueError: JSONが無効な場合
        """
        file_path = self.config_dir / file_name

        if not file_path.exists():
            raise FileNotFoundError(f"価格設定ファイルが見つかりません: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                pricing = json.load(f)

            logger.info(f"価格設定を読み込みました: {file_path} ({len(pricing)}モデル)")
            return pricing

        except json.JSONDecodeError as e:
            logger.error(f"価格設定ファイルのJSONパースに失敗: {str(e)}")
            raise ValueError(f"価格設定ファイルのJSONが無効です: {str(e)}")
        except Exception as e:
            logger.error(f"価格設定の読み込みに失敗: {str(e)}")
            raise

    def load_schema(self, file_name: str = "schema.json") -> Dict:
        """
        JSONスキーマを読み込む

        Args:
            file_name: スキーマファイル名

        Returns:
            JSONスキーマの辞書

        Raises:
            FileNotFoundError: ファイルが存在しない場合
            ValueError: JSONが無効な場合
        """
        file_path = self.config_dir / file_name

        if not file_path.exists():
            logger.warning(f"スキーマファイルが見つかりません: {file_path}")
            logger.info("スキーマ検証をスキップします")
            return {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)

            logger.info(f"JSONスキーマを読み込みました: {file_path}")
            return schema

        except json.JSONDecodeError as e:
            logger.error(f"スキーマファイルのJSONパースに失敗: {str(e)}")
            raise ValueError(f"スキーマファイルのJSONが無効です: {str(e)}")
        except Exception as e:
            logger.error(f"スキーマの読み込みに失敗: {str(e)}")
            raise

    def load_system_prompt(self, file_name: str = "system_prompt.txt") -> str:
        """
        システムプロンプトを読み込む

        Args:
            file_name: プロンプトファイル名

        Returns:
            システムプロンプトの文字列

        Raises:
            FileNotFoundError: ファイルが存在しない場合
        """
        # configディレクトリとpromptsディレクトリの両方を探す
        search_paths = [
            self.config_dir / file_name,
            self.config_dir.parent / "prompts" / file_name
        ]

        for file_path in search_paths:
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        prompt = f.read()

                    logger.info(f"システムプロンプトを読み込みました: {file_path} ({len(prompt)}文字)")
                    return prompt

                except Exception as e:
                    logger.error(f"プロンプトの読み込みに失敗: {str(e)}")
                    raise

        logger.warning(f"システムプロンプトファイルが見つかりません: {search_paths}")
        logger.info("デフォルトプロンプトを使用します")

        # デフォルトプロンプト
        default_prompt = """
あなたは不動産賃貸借契約書からデータを抽出する専門家です。
提供された契約書PDFから、指定されたJSONスキーマに従って正確にデータを抽出してください。

重要な注意事項:
1. 情報が明示的に記載されている場合のみ抽出してください
2. 推測や仮定で情報を補完しないでください
3. 数値は正確に抽出してください（単位に注意）
4. 日付はYYYY-MM-DD形式で出力してください
5. 出力は有効なJSON形式のみとしてください
""".strip()

        return default_prompt

    def validate_config(self) -> bool:
        """
        設定の妥当性を検証する

        Returns:
            すべての設定が有効な場合True
        """
        all_valid = True

        # APIキーの検証
        try:
            api_keys = self.load_api_keys()
            if not api_keys:
                logger.error("APIキーが設定されていません")
                all_valid = False
            else:
                logger.info("✓ APIキー設定OK")
        except Exception as e:
            logger.error(f"✗ APIキー設定エラー: {str(e)}")
            all_valid = False

        # 価格設定の検証
        try:
            pricing = self.load_pricing()
            if not pricing:
                logger.error("価格設定が空です")
                all_valid = False
            else:
                logger.info(f"✓ 価格設定OK ({len(pricing)}モデル)")
        except Exception as e:
            logger.error(f"✗ 価格設定エラー: {str(e)}")
            all_valid = False

        # スキーマの検証（オプション）
        try:
            schema = self.load_schema()
            if schema:
                logger.info("✓ JSONスキーマ設定OK")
            else:
                logger.warning("⚠ JSONスキーマが設定されていません（スキップ可）")
        except Exception as e:
            logger.warning(f"⚠ JSONスキーマエラー: {str(e)}")

        # プロンプトの検証（オプション）
        try:
            prompt = self.load_system_prompt()
            if prompt:
                logger.info("✓ システムプロンプト設定OK")
        except Exception as e:
            logger.warning(f"⚠ システムプロンプトエラー: {str(e)}")

        return all_valid

    def get_all_configs(self) -> Dict[str, Any]:
        """
        すべての設定を一度に読み込む

        Returns:
            すべての設定を含む辞書
        """
        configs = {}

        try:
            configs['api_keys'] = self.load_api_keys()
        except Exception as e:
            logger.error(f"APIキーの読み込み失敗: {str(e)}")
            configs['api_keys'] = {}

        try:
            configs['pricing'] = self.load_pricing()
        except Exception as e:
            logger.error(f"価格設定の読み込み失敗: {str(e)}")
            configs['pricing'] = {}

        try:
            configs['schema'] = self.load_schema()
        except Exception as e:
            logger.warning(f"スキーマの読み込み失敗: {str(e)}")
            configs['schema'] = {}

        try:
            configs['system_prompt'] = self.load_system_prompt()
        except Exception as e:
            logger.warning(f"プロンプトの読み込み失敗: {str(e)}")
            configs['system_prompt'] = ""

        return configs

    def save_config_template(self) -> None:
        """設定ファイルのテンプレートを作成する"""
        # api_keys.example.json
        api_keys_example = {
            "gemini": "YOUR_GEMINI_API_KEY_HERE",
            "openai": "YOUR_OPENAI_API_KEY_HERE",
            "anthropic": "YOUR_ANTHROPIC_API_KEY_HERE",
            "azure": {
                "endpoint": "https://YOUR_RESOURCE_NAME.cognitiveservices.azure.com/",
                "key": "YOUR_AZURE_KEY_HERE"
            }
        }

        example_path = self.config_dir / "api_keys.example.json"
        if not example_path.exists():
            with open(example_path, 'w', encoding='utf-8') as f:
                json.dump(api_keys_example, f, ensure_ascii=False, indent=2)
            logger.info(f"APIキーテンプレート作成: {example_path}")

        # system_prompt.txt
        prompt_dir = self.config_dir.parent / "prompts"
        prompt_dir.mkdir(exist_ok=True)

        prompt_path = prompt_dir / "system_prompt.txt"
        if not prompt_path.exists():
            default_prompt = self.load_system_prompt()
            with open(prompt_path, 'w', encoding='utf-8') as f:
                f.write(default_prompt)
            logger.info(f"プロンプトテンプレート作成: {prompt_path}")
