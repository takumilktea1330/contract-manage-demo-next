"""
画像変換モジュール

PDFファイルを画像に変換し、Base64エンコードやサイズ最適化を行う。
"""

import base64
import io
import logging
from pathlib import Path
from typing import List, Optional, Union
from PIL import Image
import pdf2image

logger = logging.getLogger(__name__)


class ImageConverter:
    """PDF→画像変換とBase64エンコードを行うクラス"""

    def __init__(
        self,
        dpi: int = 200,
        format: str = 'PNG',
        max_size_mb: float = 10.0
    ):
        """
        ImageConverterの初期化

        Args:
            dpi: 画像変換時の解像度（デフォルト: 200）
            format: 出力画像フォーマット（PNG, JPEG等）
            max_size_mb: 画像の最大サイズ（MB）
        """
        self.dpi = dpi
        self.format = format.upper()
        self.max_size_mb = max_size_mb

    def pdf_to_images(
        self,
        pdf_path: str,
        dpi: Optional[int] = None,
        first_page: Optional[int] = None,
        last_page: Optional[int] = None
    ) -> List[Image.Image]:
        """
        PDFファイルを画像のリストに変換する

        Args:
            pdf_path: PDFファイルのパス
            dpi: 解像度（指定がない場合は初期化時の値を使用）
            first_page: 開始ページ（1-indexed、Noneの場合は最初から）
            last_page: 終了ページ（1-indexed、Noneの場合は最後まで）

        Returns:
            PIL Imageオブジェクトのリスト

        Raises:
            FileNotFoundError: PDFファイルが存在しない場合
            Exception: PDF変換に失敗した場合
        """
        if dpi is None:
            dpi = self.dpi

        logger.info(f"PDF→画像変換開始: {pdf_path} (DPI: {dpi})")

        try:
            # PDFを画像に変換
            images = pdf2image.convert_from_path(
                pdf_path,
                dpi=dpi,
                first_page=first_page,
                last_page=last_page,
                fmt=self.format.lower()
            )

            logger.info(f"PDF→画像変換完了: {len(images)}ページ")
            return images

        except FileNotFoundError:
            logger.error(f"PDFファイルが見つかりません: {pdf_path}")
            raise
        except Exception as e:
            logger.error(f"PDF→画像変換に失敗しました: {pdf_path}, エラー: {str(e)}")
            raise Exception(f"PDF変換エラー: {str(e)}")

    def encode_image_base64(
        self,
        image: Union[Image.Image, str],
        format: Optional[str] = None
    ) -> str:
        """
        画像をBase64エンコードする

        Args:
            image: PIL Imageオブジェクトまたはファイルパス
            format: 画像フォーマット（Noneの場合は初期化時の値を使用）

        Returns:
            Base64エンコードされた文字列

        Raises:
            ValueError: 画像の処理に失敗した場合
        """
        if format is None:
            format = self.format

        try:
            # 文字列の場合はファイルパスとして扱う
            if isinstance(image, str):
                image = Image.open(image)

            # 画像をバイナリデータに変換
            buffer = io.BytesIO()
            image.save(buffer, format=format)
            buffer.seek(0)

            # Base64エンコード
            encoded = base64.b64encode(buffer.read()).decode('utf-8')

            logger.debug(f"Base64エンコード完了: {len(encoded)}文字")
            return encoded

        except Exception as e:
            logger.error(f"Base64エンコードに失敗しました: {str(e)}")
            raise ValueError(f"画像のエンコードに失敗しました: {str(e)}")

    def optimize_image_size(
        self,
        image: Image.Image,
        max_size_mb: Optional[float] = None,
        quality: int = 85,
        format: Optional[str] = None
    ) -> Image.Image:
        """
        画像のファイルサイズを最適化する

        Args:
            image: PIL Imageオブジェクト
            max_size_mb: 最大サイズ（MB）
            quality: JPEG品質（1-100）
            format: 画像フォーマット

        Returns:
            最適化された画像

        Raises:
            ValueError: 最適化に失敗した場合
        """
        if max_size_mb is None:
            max_size_mb = self.max_size_mb

        if format is None:
            format = self.format

        max_size_bytes = max_size_mb * 1024 * 1024

        try:
            # 現在のサイズをチェック
            buffer = io.BytesIO()
            save_kwargs = {}

            if format == 'JPEG':
                # RGBAをRGBに変換（JPEGは透過をサポートしない）
                if image.mode == 'RGBA':
                    # 白背景で合成
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[3])
                    image = background
                save_kwargs['quality'] = quality

            image.save(buffer, format=format, **save_kwargs)
            current_size = buffer.tell()

            logger.info(f"画像サイズ: {current_size / 1024 / 1024:.2f}MB (制限: {max_size_mb}MB)")

            # サイズが制限以下なら最適化不要
            if current_size <= max_size_bytes:
                return image

            # サイズオーバーの場合、リサイズで対応
            logger.warning(f"画像サイズが制限を超えています。リサイズを実行します。")

            scale_factor = (max_size_bytes / current_size) ** 0.5
            new_width = int(image.width * scale_factor * 0.9)  # 少し余裕を持たせる
            new_height = int(image.height * scale_factor * 0.9)

            resized_image = image.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS
            )

            # リサイズ後のサイズを確認
            buffer = io.BytesIO()
            resized_image.save(buffer, format=format, **save_kwargs)
            new_size = buffer.tell()

            logger.info(
                f"リサイズ完了: {image.width}x{image.height} → {new_width}x{new_height}, "
                f"{current_size / 1024 / 1024:.2f}MB → {new_size / 1024 / 1024:.2f}MB"
            )

            return resized_image

        except Exception as e:
            logger.error(f"画像の最適化に失敗しました: {str(e)}")
            raise ValueError(f"画像の最適化に失敗しました: {str(e)}")

    def get_image_info(self, image: Image.Image) -> dict:
        """
        画像の情報を取得する

        Args:
            image: PIL Imageオブジェクト

        Returns:
            画像情報の辞書
        """
        try:
            buffer = io.BytesIO()
            image.save(buffer, format=self.format)
            size_bytes = buffer.tell()

            info = {
                'width': image.width,
                'height': image.height,
                'mode': image.mode,
                'format': image.format or self.format,
                'size_bytes': size_bytes,
                'size_mb': size_bytes / 1024 / 1024
            }

            return info

        except Exception as e:
            logger.error(f"画像情報の取得に失敗しました: {str(e)}")
            return {}

    def save_images(
        self,
        images: List[Image.Image],
        output_dir: str,
        base_name: str,
        format: Optional[str] = None
    ) -> List[str]:
        """
        画像リストをファイルとして保存する

        Args:
            images: PIL Imageオブジェクトのリスト
            output_dir: 出力ディレクトリ
            base_name: ベースファイル名
            format: 画像フォーマット

        Returns:
            保存されたファイルパスのリスト

        Raises:
            Exception: 保存に失敗した場合
        """
        if format is None:
            format = self.format

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        saved_paths = []

        try:
            for i, image in enumerate(images, start=1):
                file_name = f"{base_name}_page_{i:03d}.{format.lower()}"
                file_path = output_path / file_name

                save_kwargs = {}
                if format == 'JPEG':
                    # RGBAをRGBに変換
                    if image.mode == 'RGBA':
                        background = Image.new('RGB', image.size, (255, 255, 255))
                        background.paste(image, mask=image.split()[3])
                        image = background
                    save_kwargs['quality'] = 85

                image.save(str(file_path), format=format, **save_kwargs)
                saved_paths.append(str(file_path))

                logger.info(f"画像を保存しました: {file_path}")

            logger.info(f"全ての画像を保存しました: {len(saved_paths)}ファイル")
            return saved_paths

        except Exception as e:
            logger.error(f"画像の保存に失敗しました: {str(e)}")
            raise Exception(f"画像保存エラー: {str(e)}")

    def pdf_to_base64_images(
        self,
        pdf_path: str,
        optimize: bool = True,
        dpi: Optional[int] = None
    ) -> List[str]:
        """
        PDFファイルをBase64エンコードされた画像のリストに変換する
        （pdf_to_imagesとencode_image_base64を組み合わせた便利メソッド）

        Args:
            pdf_path: PDFファイルのパス
            optimize: サイズ最適化を行うか
            dpi: 解像度

        Returns:
            Base64エンコードされた画像のリスト

        Raises:
            Exception: 変換に失敗した場合
        """
        try:
            # PDFを画像に変換
            images = self.pdf_to_images(pdf_path, dpi=dpi)

            # Base64エンコード
            encoded_images = []
            for i, image in enumerate(images, start=1):
                # 最適化
                if optimize:
                    image = self.optimize_image_size(image)

                # エンコード
                encoded = self.encode_image_base64(image)
                encoded_images.append(encoded)

                logger.info(f"ページ {i}/{len(images)} をエンコードしました")

            logger.info(f"PDF→Base64変換完了: {len(encoded_images)}ページ")
            return encoded_images

        except Exception as e:
            logger.error(f"PDF→Base64変換に失敗しました: {pdf_path}, エラー: {str(e)}")
            raise
