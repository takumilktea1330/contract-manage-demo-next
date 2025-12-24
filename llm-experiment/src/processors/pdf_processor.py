"""
PDF処理モジュール

PDFファイルの読み込み、検証、基本情報の取得を行う。
"""

import os
from pathlib import Path
from typing import Optional, Tuple
import PyPDF2
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    """PDFファイルの基本的な処理を行うクラス"""

    def __init__(self):
        """PDFProcessorの初期化"""
        self.current_pdf_path: Optional[str] = None
        self.current_pdf_reader: Optional[PyPDF2.PdfReader] = None

    def load_pdf(self, pdf_path: str) -> bytes:
        """
        PDFファイルを読み込んでバイナリデータとして返す

        Args:
            pdf_path: PDFファイルのパス

        Returns:
            PDFファイルのバイナリデータ

        Raises:
            FileNotFoundError: ファイルが存在しない場合
            ValueError: PDFファイルが無効な場合
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")

        if not pdf_path.lower().endswith('.pdf'):
            raise ValueError(f"PDFファイルではありません: {pdf_path}")

        try:
            with open(pdf_path, 'rb') as file:
                pdf_data = file.read()

            # PDFとして有効か簡易チェック
            if not pdf_data.startswith(b'%PDF-'):
                raise ValueError(f"有効なPDFファイルではありません: {pdf_path}")

            self.current_pdf_path = pdf_path
            logger.info(f"PDFファイルを読み込みました: {pdf_path} ({len(pdf_data)} bytes)")

            return pdf_data

        except Exception as e:
            logger.error(f"PDFファイルの読み込みに失敗しました: {pdf_path}, エラー: {str(e)}")
            raise

    def get_page_count(self, pdf_path: Optional[str] = None) -> int:
        """
        PDFファイルのページ数を取得する

        Args:
            pdf_path: PDFファイルのパス（Noneの場合は最後に読み込んだファイル）

        Returns:
            ページ数

        Raises:
            ValueError: PDFファイルが指定されていない、または無効な場合
        """
        if pdf_path is None:
            pdf_path = self.current_pdf_path

        if pdf_path is None:
            raise ValueError("PDFファイルが指定されていません")

        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)

            logger.info(f"ページ数: {page_count} ({pdf_path})")
            return page_count

        except Exception as e:
            logger.error(f"ページ数の取得に失敗しました: {pdf_path}, エラー: {str(e)}")
            raise ValueError(f"PDFファイルの処理に失敗しました: {str(e)}")

    def validate_pdf(self, pdf_path: str) -> Tuple[bool, Optional[str]]:
        """
        PDFファイルの有効性を検証する

        Args:
            pdf_path: PDFファイルのパス

        Returns:
            (検証結果, エラーメッセージ) のタプル
            検証成功時は (True, None)、失敗時は (False, エラーメッセージ)
        """
        # ファイルの存在確認
        if not os.path.exists(pdf_path):
            return False, f"ファイルが存在しません: {pdf_path}"

        # 拡張子確認
        if not pdf_path.lower().endswith('.pdf'):
            return False, f"PDFファイルではありません: {pdf_path}"

        # ファイルサイズ確認
        file_size = os.path.getsize(pdf_path)
        if file_size == 0:
            return False, "ファイルサイズが0バイトです"

        # PDFとして読み込めるか確認
        try:
            with open(pdf_path, 'rb') as file:
                # PDFヘッダー確認
                header = file.read(5)
                if not header.startswith(b'%PDF-'):
                    return False, "有効なPDFヘッダーがありません"

                # PyPDF2で読み込めるか確認
                file.seek(0)
                pdf_reader = PyPDF2.PdfReader(file)

                # ページ数確認
                page_count = len(pdf_reader.pages)
                if page_count == 0:
                    return False, "ページが存在しません"

                # 暗号化確認
                if pdf_reader.is_encrypted:
                    logger.warning(f"PDFファイルは暗号化されています: {pdf_path}")
                    return False, "暗号化されたPDFファイルは処理できません"

            logger.info(f"PDFファイルの検証成功: {pdf_path} ({page_count}ページ, {file_size}バイト)")
            return True, None

        except Exception as e:
            error_msg = f"PDFファイルの検証に失敗しました: {str(e)}"
            logger.error(f"{error_msg} ({pdf_path})")
            return False, error_msg

    def get_pdf_metadata(self, pdf_path: Optional[str] = None) -> dict:
        """
        PDFファイルのメタデータを取得する

        Args:
            pdf_path: PDFファイルのパス（Noneの場合は最後に読み込んだファイル）

        Returns:
            メタデータの辞書
        """
        if pdf_path is None:
            pdf_path = self.current_pdf_path

        if pdf_path is None:
            raise ValueError("PDFファイルが指定されていません")

        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                metadata = {
                    'page_count': len(pdf_reader.pages),
                    'file_name': Path(pdf_path).name,
                    'file_size': os.path.getsize(pdf_path),
                    'is_encrypted': pdf_reader.is_encrypted,
                }

                # PDF情報があれば追加
                if pdf_reader.metadata:
                    pdf_info = pdf_reader.metadata
                    if pdf_info.title:
                        metadata['title'] = pdf_info.title
                    if pdf_info.author:
                        metadata['author'] = pdf_info.author
                    if pdf_info.creator:
                        metadata['creator'] = pdf_info.creator
                    if pdf_info.producer:
                        metadata['producer'] = pdf_info.producer
                    if pdf_info.creation_date:
                        metadata['creation_date'] = str(pdf_info.creation_date)
                    if pdf_info.modification_date:
                        metadata['modification_date'] = str(pdf_info.modification_date)

            logger.info(f"メタデータを取得しました: {pdf_path}")
            return metadata

        except Exception as e:
            logger.error(f"メタデータの取得に失敗しました: {pdf_path}, エラー: {str(e)}")
            return {}

    def extract_text(self, pdf_path: Optional[str] = None, page_numbers: Optional[list] = None) -> str:
        """
        PDFファイルからテキストを抽出する

        Args:
            pdf_path: PDFファイルのパス（Noneの場合は最後に読み込んだファイル）
            page_numbers: 抽出するページ番号のリスト（Noneの場合は全ページ）

        Returns:
            抽出されたテキスト
        """
        if pdf_path is None:
            pdf_path = self.current_pdf_path

        if pdf_path is None:
            raise ValueError("PDFファイルが指定されていません")

        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)

                # ページ番号の指定がない場合は全ページ
                if page_numbers is None:
                    page_numbers = range(total_pages)

                extracted_text = []
                for page_num in page_numbers:
                    if 0 <= page_num < total_pages:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        extracted_text.append(f"--- Page {page_num + 1} ---\n{text}\n")
                    else:
                        logger.warning(f"ページ番号が範囲外です: {page_num} (総ページ数: {total_pages})")

                result = '\n'.join(extracted_text)
                logger.info(f"テキストを抽出しました: {pdf_path} ({len(result)}文字)")
                return result

        except Exception as e:
            logger.error(f"テキストの抽出に失敗しました: {pdf_path}, エラー: {str(e)}")
            raise ValueError(f"テキストの抽出に失敗しました: {str(e)}")
