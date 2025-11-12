"""
PDF処理モジュールのテスト
"""

import pytest
import os
import tempfile
from pathlib import Path
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processors import PDFProcessor


class TestPDFProcessor:
    """PDFProcessorクラスのテスト"""

    @pytest.fixture
    def processor(self):
        """PDFProcessorのインスタンスを返す"""
        return PDFProcessor()

    @pytest.fixture
    def sample_pdf_path(self):
        """サンプルPDFのパスを返す（存在する場合）"""
        # テスト用PDFが存在する場合はそのパスを返す
        test_pdf = Path(__file__).parent.parent / "data" / "input" / "sample.pdf"
        if test_pdf.exists():
            return str(test_pdf)
        return None

    def test_processor_initialization(self, processor):
        """PDFProcessorの初期化テスト"""
        assert processor is not None
        assert processor.current_pdf_path is None
        assert processor.current_pdf_reader is None

    def test_validate_pdf_nonexistent_file(self, processor):
        """存在しないファイルの検証テスト"""
        is_valid, error_msg = processor.validate_pdf("nonexistent.pdf")
        assert is_valid is False
        assert "存在しません" in error_msg

    def test_validate_pdf_wrong_extension(self, processor):
        """PDFではないファイルの検証テスト"""
        # 一時的なテキストファイルを作成
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"This is not a PDF")
            tmp_path = tmp.name

        try:
            is_valid, error_msg = processor.validate_pdf(tmp_path)
            assert is_valid is False
            assert "PDFファイルではありません" in error_msg
        finally:
            os.unlink(tmp_path)

    def test_validate_pdf_empty_file(self, processor):
        """空のファイルの検証テスト"""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            is_valid, error_msg = processor.validate_pdf(tmp_path)
            assert is_valid is False
            assert "0バイト" in error_msg
        finally:
            os.unlink(tmp_path)

    def test_load_pdf_nonexistent(self, processor):
        """存在しないPDFの読み込みテスト"""
        with pytest.raises(FileNotFoundError):
            processor.load_pdf("nonexistent.pdf")

    def test_get_page_count_no_pdf_loaded(self, processor):
        """PDFが読み込まれていない状態でのページ数取得テスト"""
        with pytest.raises(ValueError):
            processor.get_page_count()

    @pytest.mark.skipif(
        not Path(__file__).parent.parent.joinpath("data/input/sample.pdf").exists(),
        reason="サンプルPDFが存在しません"
    )
    def test_load_pdf_success(self, processor, sample_pdf_path):
        """正常なPDF読み込みテスト"""
        if sample_pdf_path:
            pdf_data = processor.load_pdf(sample_pdf_path)
            assert pdf_data is not None
            assert len(pdf_data) > 0
            assert pdf_data.startswith(b'%PDF-')
            assert processor.current_pdf_path == sample_pdf_path

    @pytest.mark.skipif(
        not Path(__file__).parent.parent.joinpath("data/input/sample.pdf").exists(),
        reason="サンプルPDFが存在しません"
    )
    def test_get_page_count_success(self, processor, sample_pdf_path):
        """正常なページ数取得テスト"""
        if sample_pdf_path:
            page_count = processor.get_page_count(sample_pdf_path)
            assert page_count > 0
            assert isinstance(page_count, int)

    @pytest.mark.skipif(
        not Path(__file__).parent.parent.joinpath("data/input/sample.pdf").exists(),
        reason="サンプルPDFが存在しません"
    )
    def test_validate_pdf_success(self, processor, sample_pdf_path):
        """正常なPDF検証テスト"""
        if sample_pdf_path:
            is_valid, error_msg = processor.validate_pdf(sample_pdf_path)
            assert is_valid is True
            assert error_msg is None

    @pytest.mark.skipif(
        not Path(__file__).parent.parent.joinpath("data/input/sample.pdf").exists(),
        reason="サンプルPDFが存在しません"
    )
    def test_get_pdf_metadata(self, processor, sample_pdf_path):
        """PDFメタデータ取得テスト"""
        if sample_pdf_path:
            metadata = processor.get_pdf_metadata(sample_pdf_path)
            assert isinstance(metadata, dict)
            assert 'page_count' in metadata
            assert 'file_name' in metadata
            assert 'file_size' in metadata
            assert metadata['page_count'] > 0
            assert metadata['file_size'] > 0

    @pytest.mark.skipif(
        not Path(__file__).parent.parent.joinpath("data/input/sample.pdf").exists(),
        reason="サンプルPDFが存在しません"
    )
    def test_extract_text(self, processor, sample_pdf_path):
        """テキスト抽出テスト"""
        if sample_pdf_path:
            text = processor.extract_text(sample_pdf_path)
            assert isinstance(text, str)
            assert len(text) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
