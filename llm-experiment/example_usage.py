"""
PDF処理モジュールの使用例

このスクリプトは、PDFProcessorとImageConverterの基本的な使い方を示します。
"""

import sys
import logging
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.processors import PDFProcessor, ImageConverter

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_pdf_processor():
    """PDFProcessorの使用例"""
    logger.info("=" * 60)
    logger.info("PDFProcessor の使用例")
    logger.info("=" * 60)

    # PDFProcessorのインスタンス化
    processor = PDFProcessor()

    # サンプルPDFのパス
    pdf_path = "data/input/sample.pdf"

    # 1. PDFファイルの検証
    logger.info("\n1. PDFファイルの検証")
    is_valid, error_msg = processor.validate_pdf(pdf_path)
    if is_valid:
        logger.info(f"✓ PDFファイルは有効です: {pdf_path}")
    else:
        logger.error(f"✗ PDFファイルは無効です: {error_msg}")
        return

    # 2. PDFファイルの読み込み
    logger.info("\n2. PDFファイルの読み込み")
    try:
        pdf_data = processor.load_pdf(pdf_path)
        logger.info(f"✓ PDFファイルを読み込みました: {len(pdf_data)} bytes")
    except Exception as e:
        logger.error(f"✗ PDFファイルの読み込みに失敗: {str(e)}")
        return

    # 3. ページ数の取得
    logger.info("\n3. ページ数の取得")
    try:
        page_count = processor.get_page_count(pdf_path)
        logger.info(f"✓ ページ数: {page_count}")
    except Exception as e:
        logger.error(f"✗ ページ数の取得に失敗: {str(e)}")

    # 4. メタデータの取得
    logger.info("\n4. メタデータの取得")
    try:
        metadata = processor.get_pdf_metadata(pdf_path)
        logger.info(f"✓ メタデータ:")
        for key, value in metadata.items():
            logger.info(f"  - {key}: {value}")
    except Exception as e:
        logger.error(f"✗ メタデータの取得に失敗: {str(e)}")

    # 5. テキストの抽出
    logger.info("\n5. テキストの抽出（最初の1ページ）")
    try:
        text = processor.extract_text(pdf_path, page_numbers=[0])
        logger.info(f"✓ テキストを抽出しました: {len(text)} 文字")
        logger.info(f"  最初の100文字: {text[:100]}...")
    except Exception as e:
        logger.error(f"✗ テキストの抽出に失敗: {str(e)}")


def example_image_converter():
    """ImageConverterの使用例"""
    logger.info("\n" + "=" * 60)
    logger.info("ImageConverter の使用例")
    logger.info("=" * 60)

    # ImageConverterのインスタンス化
    converter = ImageConverter(dpi=150, format='PNG', max_size_mb=5.0)

    # サンプルPDFのパス
    pdf_path = "data/input/sample.pdf"

    # 1. PDFを画像に変換
    logger.info("\n1. PDFを画像に変換")
    try:
        images = converter.pdf_to_images(pdf_path, dpi=150)
        logger.info(f"✓ {len(images)} ページの画像に変換しました")

        # 最初の画像の情報を表示
        if images:
            info = converter.get_image_info(images[0])
            logger.info(f"  最初のページの情報:")
            logger.info(f"    - サイズ: {info['width']}x{info['height']} px")
            logger.info(f"    - モード: {info['mode']}")
            logger.info(f"    - ファイルサイズ: {info['size_mb']:.2f} MB")

    except Exception as e:
        logger.error(f"✗ PDF→画像変換に失敗: {str(e)}")
        return

    # 2. Base64エンコード
    logger.info("\n2. Base64エンコード")
    try:
        if images:
            encoded = converter.encode_image_base64(images[0])
            logger.info(f"✓ Base64エンコード完了: {len(encoded)} 文字")
            logger.info(f"  最初の50文字: {encoded[:50]}...")
    except Exception as e:
        logger.error(f"✗ Base64エンコードに失敗: {str(e)}")

    # 3. 画像の最適化
    logger.info("\n3. 画像の最適化")
    try:
        if images:
            original_info = converter.get_image_info(images[0])
            optimized = converter.optimize_image_size(images[0], max_size_mb=1.0)
            optimized_info = converter.get_image_info(optimized)

            logger.info(f"✓ 画像を最適化しました:")
            logger.info(f"  元のサイズ: {original_info['size_mb']:.2f} MB "
                       f"({original_info['width']}x{original_info['height']})")
            logger.info(f"  最適化後: {optimized_info['size_mb']:.2f} MB "
                       f"({optimized_info['width']}x{optimized_info['height']})")
    except Exception as e:
        logger.error(f"✗ 画像の最適化に失敗: {str(e)}")

    # 4. 画像の保存
    logger.info("\n4. 画像の保存")
    try:
        if images:
            output_dir = "output/images"
            saved_paths = converter.save_images(
                images[:2],  # 最初の2ページのみ
                output_dir=output_dir,
                base_name="sample",
                format='PNG'
            )
            logger.info(f"✓ {len(saved_paths)} 枚の画像を保存しました:")
            for path in saved_paths:
                logger.info(f"  - {path}")
    except Exception as e:
        logger.error(f"✗ 画像の保存に失敗: {str(e)}")

    # 5. PDF→Base64の一括変換
    logger.info("\n5. PDF→Base64の一括変換")
    try:
        encoded_images = converter.pdf_to_base64_images(
            pdf_path,
            optimize=True,
            dpi=100
        )
        logger.info(f"✓ {len(encoded_images)} ページをBase64に変換しました")
        for i, encoded in enumerate(encoded_images, start=1):
            logger.info(f"  - ページ {i}: {len(encoded)} 文字")
    except Exception as e:
        logger.error(f"✗ PDF→Base64変換に失敗: {str(e)}")


def main():
    """メイン関数"""
    logger.info("PDF処理モジュールの使用例を実行します")

    # PDFファイルの確認
    pdf_path = Path("data/input/sample.pdf")
    if not pdf_path.exists():
        logger.warning(f"\n警告: サンプルPDFが見つかりません: {pdf_path}")
        logger.warning("data/input/sample.pdf を配置してから実行してください。")
        logger.warning("それでも動作確認のために、存在しないファイルでのエラー処理を確認します。\n")

    # PDFProcessorの使用例
    example_pdf_processor()

    # ImageConverterの使用例
    example_image_converter()

    logger.info("\n" + "=" * 60)
    logger.info("使用例の実行が完了しました")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
