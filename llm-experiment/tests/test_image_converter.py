"""
画像変換モジュールのテスト
"""

import pytest
import os
import tempfile
from pathlib import Path
import sys
from PIL import Image

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processors import ImageConverter


class TestImageConverter:
    """ImageConverterクラスのテスト"""

    @pytest.fixture
    def converter(self):
        """ImageConverterのインスタンスを返す"""
        return ImageConverter(dpi=150, format='PNG', max_size_mb=5.0)

    @pytest.fixture
    def sample_image(self):
        """テスト用のサンプル画像を作成"""
        # 100x100の白い画像を作成
        img = Image.new('RGB', (100, 100), color='white')
        return img

    @pytest.fixture
    def sample_pdf_path(self):
        """サンプルPDFのパスを返す（存在する場合）"""
        test_pdf = Path(__file__).parent.parent / "data" / "input" / "sample.pdf"
        if test_pdf.exists():
            return str(test_pdf)
        return None

    def test_converter_initialization(self, converter):
        """ImageConverterの初期化テスト"""
        assert converter is not None
        assert converter.dpi == 150
        assert converter.format == 'PNG'
        assert converter.max_size_mb == 5.0

    def test_encode_image_base64(self, converter, sample_image):
        """Base64エンコードテスト"""
        encoded = converter.encode_image_base64(sample_image)
        assert isinstance(encoded, str)
        assert len(encoded) > 0
        # Base64は英数字と+/=のみ
        assert all(c.isalnum() or c in '+/=' for c in encoded)

    def test_get_image_info(self, converter, sample_image):
        """画像情報取得テスト"""
        info = converter.get_image_info(sample_image)
        assert isinstance(info, dict)
        assert info['width'] == 100
        assert info['height'] == 100
        assert info['mode'] == 'RGB'
        assert info['size_bytes'] > 0
        assert info['size_mb'] > 0

    def test_optimize_image_size_no_change(self, converter, sample_image):
        """サイズ最適化（変更不要）テスト"""
        # 小さい画像なので最適化の必要なし
        optimized = converter.optimize_image_size(sample_image, max_size_mb=10.0)
        assert optimized is not None
        assert isinstance(optimized, Image.Image)

    def test_optimize_image_size_with_resize(self, converter):
        """サイズ最適化（リサイズ必要）テスト"""
        # 大きめの画像を作成
        large_image = Image.new('RGB', (4000, 4000), color='white')

        # 非常に小さいサイズ制限を設定してリサイズを強制
        optimized = converter.optimize_image_size(large_image, max_size_mb=0.01)
        assert optimized is not None
        assert isinstance(optimized, Image.Image)
        # リサイズされているはず
        assert optimized.width < large_image.width
        assert optimized.height < large_image.height

    def test_optimize_image_rgba_to_rgb(self, converter):
        """RGBA→RGB変換テスト（JPEG用）"""
        # RGBA画像を作成
        rgba_image = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))

        # JPEGフォーマットで最適化（RGBに変換される）
        optimized = converter.optimize_image_size(rgba_image, format='JPEG')
        assert optimized is not None
        assert optimized.mode == 'RGB'

    def test_save_images(self, converter, sample_image):
        """画像保存テスト"""
        with tempfile.TemporaryDirectory() as tmpdir:
            images = [sample_image, sample_image]
            saved_paths = converter.save_images(
                images,
                output_dir=tmpdir,
                base_name="test",
                format='PNG'
            )

            assert len(saved_paths) == 2
            for path in saved_paths:
                assert os.path.exists(path)
                assert path.endswith('.png')

    @pytest.mark.skipif(
        not Path(__file__).parent.parent.joinpath("data/input/sample.pdf").exists(),
        reason="サンプルPDFが存在しません"
    )
    def test_pdf_to_images(self, converter, sample_pdf_path):
        """PDF→画像変換テスト"""
        if sample_pdf_path:
            images = converter.pdf_to_images(sample_pdf_path, dpi=100)
            assert isinstance(images, list)
            assert len(images) > 0
            for img in images:
                assert isinstance(img, Image.Image)
                assert img.width > 0
                assert img.height > 0

    @pytest.mark.skipif(
        not Path(__file__).parent.parent.joinpath("data/input/sample.pdf").exists(),
        reason="サンプルPDFが存在しません"
    )
    def test_pdf_to_base64_images(self, converter, sample_pdf_path):
        """PDF→Base64変換テスト"""
        if sample_pdf_path:
            encoded_images = converter.pdf_to_base64_images(
                sample_pdf_path,
                optimize=True,
                dpi=100
            )
            assert isinstance(encoded_images, list)
            assert len(encoded_images) > 0
            for encoded in encoded_images:
                assert isinstance(encoded, str)
                assert len(encoded) > 0

    def test_pdf_to_images_nonexistent(self, converter):
        """存在しないPDFの変換テスト"""
        with pytest.raises(FileNotFoundError):
            converter.pdf_to_images("nonexistent.pdf")

    def test_encode_image_from_file(self, converter, sample_image):
        """ファイルパスからのBase64エンコードテスト"""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            sample_image.save(tmp.name, format='PNG')
            tmp_path = tmp.name

        try:
            encoded = converter.encode_image_base64(tmp_path)
            assert isinstance(encoded, str)
            assert len(encoded) > 0
        finally:
            os.unlink(tmp_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
