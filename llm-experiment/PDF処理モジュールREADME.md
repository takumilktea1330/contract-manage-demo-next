# PDF処理モジュール

不動産賃貸借契約書のPDFから構造化データを抽出するためのPDF処理モジュールです。

## 機能

### PDFProcessor
- PDFファイルの読み込みとバイナリデータ取得
- PDFファイルの検証（存在確認、形式確認、暗号化確認）
- ページ数の取得
- メタデータの取得（ファイル情報、作成日時など）
- テキストの抽出

### ImageConverter
- PDFファイルを画像に変換（各ページを個別の画像として）
- 画像のBase64エンコード
- 画像サイズの最適化（リサイズ、圧縮）
- 画像ファイルの保存
- PDF→Base64の一括変換

## インストール

### 必要なシステム依存パッケージ

PDF処理には`poppler`が必要です。

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install poppler-utils
```

#### macOS
```bash
brew install poppler
```

#### Windows
1. [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/)からダウンロード
2. 環境変数のPATHに追加

### Pythonパッケージのインストール

```bash
pip install -r requirements.txt
```

主要なパッケージ:
- `PyPDF2`: PDF読み込みとメタデータ抽出
- `pdf2image`: PDF→画像変換
- `Pillow`: 画像処理

## 使用方法

### 基本的な使い方

#### PDFProcessor

```python
from src.processors import PDFProcessor

# インスタンス化
processor = PDFProcessor()

# PDFファイルの検証
is_valid, error_msg = processor.validate_pdf("contract.pdf")
if is_valid:
    print("PDFファイルは有効です")
else:
    print(f"エラー: {error_msg}")

# PDFファイルの読み込み
pdf_data = processor.load_pdf("contract.pdf")

# ページ数の取得
page_count = processor.get_page_count("contract.pdf")
print(f"ページ数: {page_count}")

# メタデータの取得
metadata = processor.get_pdf_metadata("contract.pdf")
print(f"ファイル名: {metadata['file_name']}")
print(f"ファイルサイズ: {metadata['file_size']} bytes")

# テキストの抽出（全ページ）
text = processor.extract_text("contract.pdf")

# テキストの抽出（特定のページ）
text = processor.extract_text("contract.pdf", page_numbers=[0, 1, 2])
```

#### ImageConverter

```python
from src.processors import ImageConverter

# インスタンス化（パラメータ設定）
converter = ImageConverter(
    dpi=200,           # 解像度
    format='PNG',      # 出力フォーマット
    max_size_mb=10.0   # 最大ファイルサイズ
)

# PDFを画像に変換
images = converter.pdf_to_images("contract.pdf", dpi=200)
print(f"{len(images)} ページの画像に変換しました")

# 画像をBase64エンコード
encoded = converter.encode_image_base64(images[0])

# 画像の最適化
optimized = converter.optimize_image_size(images[0], max_size_mb=5.0)

# 画像の保存
saved_paths = converter.save_images(
    images,
    output_dir="output/images",
    base_name="contract",
    format='PNG'
)

# PDF→Base64の一括変換（便利メソッド）
encoded_images = converter.pdf_to_base64_images(
    "contract.pdf",
    optimize=True,  # サイズ最適化を行う
    dpi=150
)
```

### 実用例

#### LLM APIに送信する画像データの準備

```python
from src.processors import ImageConverter

# PDFをBase64エンコードされた画像リストに変換
converter = ImageConverter(dpi=200, max_size_mb=5.0)
encoded_images = converter.pdf_to_base64_images(
    "contract.pdf",
    optimize=True
)

# LLM APIに送信
for i, encoded_image in enumerate(encoded_images):
    # OpenAI Vision API の例
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{encoded_image}"
                    }
                },
                {
                    "type": "text",
                    "text": "この契約書からデータを抽出してください"
                }
            ]
        }
    ]
    # API呼び出し...
```

## テスト

### テストの実行

```bash
# すべてのテストを実行
pytest tests/

# 特定のテストファイルを実行
pytest tests/test_pdf_processor.py -v
pytest tests/test_image_converter.py -v

# カバレッジを含めて実行
pytest tests/ --cov=src/processors --cov-report=html
```

### サンプルPDFの準備

テストを完全に実行するには、サンプルPDFが必要です。

```bash
# ディレクトリ作成
mkdir -p data/input

# サンプルPDFを配置
cp /path/to/your/sample.pdf data/input/sample.pdf
```

## 使用例スクリプト

`example_usage.py`を実行すると、両モジュールの使用例を確認できます。

```bash
python example_usage.py
```

## トラブルシューティング

### Popplerが見つからないエラー

```
PDFInfoNotInstalledError: Unable to get page count. Is poppler installed and in PATH?
```

**解決方法:**
1. Popplerをインストール（上記「インストール」セクション参照）
2. 環境変数のPATHに追加されているか確認

### メモリ不足エラー

大きなPDFや高解像度での変換時にメモリ不足になる場合があります。

**解決方法:**
1. DPIを下げる（例: 200 → 100）
2. ページ毎に処理する
3. `max_size_mb`を小さくして自動リサイズを有効化

```python
# ページ毎に処理する例
converter = ImageConverter(dpi=100)
for page_num in range(1, page_count + 1):
    images = converter.pdf_to_images(
        pdf_path,
        first_page=page_num,
        last_page=page_num
    )
    # 処理...
```

### 暗号化されたPDFのエラー

暗号化されたPDFは処理できません。

**解決方法:**
1. PDFの暗号化を解除する
2. パスワードで保護されている場合は、PyPDF2で解除してから処理

```python
import PyPDF2

# パスワード保護されたPDFを開く
with open('encrypted.pdf', 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    if reader.is_encrypted:
        reader.decrypt('password')

    # 暗号化解除版を保存
    writer = PyPDF2.PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    with open('decrypted.pdf', 'wb') as output:
        writer.write(output)
```

## パフォーマンスチューニング

### DPIの選択

| DPI | 用途 | ファイルサイズ | 処理時間 |
|-----|------|--------------|---------|
| 72-100 | プレビュー、軽量処理 | 小 | 高速 |
| 150-200 | 標準的なOCR・抽出 | 中 | 中程度 |
| 300以上 | 高精度OCR、印刷品質 | 大 | 低速 |

推奨: **150-200 DPI** （精度と速度のバランスが良い）

### 画像フォーマットの選択

| フォーマット | 特徴 | 推奨用途 |
|------------|------|---------|
| PNG | ロスレス、透過対応 | テキスト中心のドキュメント |
| JPEG | 非可逆圧縮、小サイズ | 写真が多いドキュメント |

### バッチ処理

複数のPDFを処理する場合:

```python
from pathlib import Path
from src.processors import ImageConverter

converter = ImageConverter(dpi=150, max_size_mb=5.0)

pdf_files = Path("data/input").glob("*.pdf")
for pdf_path in pdf_files:
    print(f"処理中: {pdf_path.name}")
    try:
        encoded_images = converter.pdf_to_base64_images(
            str(pdf_path),
            optimize=True
        )
        # 処理...
    except Exception as e:
        print(f"エラー: {pdf_path.name}, {str(e)}")
        continue
```

## ライセンス

このプロジェクトは実験用です。

## 関連ドキュメント

- [実験手順書.md](実験手順書.md) - 実験全体の計画
- [実験スクリプト要件定義.md](実験スクリプト要件定義.md) - システム全体の要件
