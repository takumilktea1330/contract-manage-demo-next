"""
結果可視化モジュール

実験結果をグラフや図表として可視化する。
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import numpy as np

logger = logging.getLogger(__name__)

# 日本語フォントの設定
def setup_japanese_font():
    """日本語フォントの設定"""
    try:
        # 利用可能な日本語フォントを探す
        japanese_fonts = [
            'IPAexGothic', 'IPAGothic', 'Noto Sans CJK JP',
            'Hiragino Sans', 'Yu Gothic', 'MS Gothic'
        ]

        available_fonts = [f.name for f in fm.fontManager.ttflist]

        for font in japanese_fonts:
            if font in available_fonts:
                plt.rcParams['font.family'] = font
                logger.info(f"日本語フォント設定: {font}")
                return

        logger.warning("日本語フォントが見つかりません。デフォルトフォントを使用します。")
    except Exception as e:
        logger.warning(f"フォント設定に失敗しました: {str(e)}")

# モジュール読み込み時にフォント設定
setup_japanese_font()

# スタイル設定
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['figure.dpi'] = 100


class ResultVisualizer:
    """実験結果を可視化するクラス"""

    def __init__(self, output_dir: str = "output/visualizations"):
        """
        ResultVisualizerの初期化

        Args:
            output_dir: 可視化結果の出力ディレクトリ
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # カラーパレット
        self.colors = sns.color_palette("husl", 8)

        logger.info(f"ResultVisualizer初期化完了: {self.output_dir}")

    def load_summary(self, summary_path: str) -> Dict:
        """
        サマリーレポートを読み込む

        Args:
            summary_path: サマリーファイルのパス

        Returns:
            サマリーデータ
        """
        with open(summary_path, 'r', encoding='utf-8') as f:
            summary = json.load(f)

        logger.info(f"サマリー読み込み: {summary_path}")
        return summary

    def load_metrics_csv(self, csv_path: str) -> pd.DataFrame:
        """
        メトリクスCSVを読み込む

        Args:
            csv_path: CSVファイルのパス

        Returns:
            メトリクスのDataFrame
        """
        df = pd.read_csv(csv_path)
        logger.info(f"メトリクスCSV読み込み: {csv_path} ({len(df)}行)")
        return df

    def plot_accuracy_comparison(
        self,
        summary: Dict,
        save_path: Optional[str] = None
    ) -> str:
        """
        モデル別の精度比較グラフを作成する

        Args:
            summary: サマリーデータ
            save_path: 保存先パス

        Returns:
            保存したファイルパス
        """
        if save_path is None:
            save_path = self.output_dir / "accuracy_comparison.png"
        else:
            save_path = Path(save_path)

        models = summary['models']
        model_names = list(models.keys())

        # データの準備
        field_accuracy = [models[m]['avg_field_accuracy'] for m in model_names]
        f1_scores = [models[m]['avg_f1_score'] for m in model_names]

        # グラフの作成
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # 項目正答率
        bars1 = ax1.bar(model_names, field_accuracy, color=self.colors[:len(model_names)])
        ax1.set_xlabel('Model', fontsize=12)
        ax1.set_ylabel('Field Accuracy', fontsize=12)
        ax1.set_title('Average Field Accuracy by Model', fontsize=14, fontweight='bold')
        ax1.set_ylim(0, 1.0)
        ax1.tick_params(axis='x', rotation=45)

        # 値をバーの上に表示
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2%}',
                    ha='center', va='bottom', fontsize=10)

        # F1スコア
        bars2 = ax2.bar(model_names, f1_scores, color=self.colors[:len(model_names)])
        ax2.set_xlabel('Model', fontsize=12)
        ax2.set_ylabel('F1 Score', fontsize=12)
        ax2.set_title('Average F1 Score by Model', fontsize=14, fontweight='bold')
        ax2.set_ylim(0, 1.0)
        ax2.tick_params(axis='x', rotation=45)

        # 値をバーの上に表示
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.4f}',
                    ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"精度比較グラフ保存: {save_path}")
        return str(save_path)

    def plot_cost_vs_accuracy(
        self,
        summary: Dict,
        save_path: Optional[str] = None
    ) -> str:
        """
        コスト vs 精度の散布図を作成する

        Args:
            summary: サマリーデータ
            save_path: 保存先パス

        Returns:
            保存したファイルパス
        """
        if save_path is None:
            save_path = self.output_dir / "cost_vs_accuracy.png"
        else:
            save_path = Path(save_path)

        models = summary['models']
        model_names = list(models.keys())

        # データの準備
        costs = [models[m]['avg_cost_per_pdf'] for m in model_names]
        accuracies = [models[m]['avg_field_accuracy'] for m in model_names]

        # グラフの作成
        fig, ax = plt.subplots(figsize=(10, 8))

        scatter = ax.scatter(costs, accuracies, s=200, c=range(len(model_names)),
                           cmap='viridis', alpha=0.7, edgecolors='black', linewidth=2)

        # モデル名をラベルとして表示
        for i, name in enumerate(model_names):
            ax.annotate(name, (costs[i], accuracies[i]),
                       xytext=(10, 10), textcoords='offset points',
                       fontsize=10, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.3))

        ax.set_xlabel('Average Cost per PDF (JPY)', fontsize=12)
        ax.set_ylabel('Average Field Accuracy', fontsize=12)
        ax.set_title('Cost vs Accuracy Trade-off', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Y軸を0-1の範囲に設定
        ax.set_ylim(0, 1.0)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"コスト vs 精度グラフ保存: {save_path}")
        return str(save_path)

    def plot_response_time_comparison(
        self,
        summary: Dict,
        save_path: Optional[str] = None
    ) -> str:
        """
        レスポンスタイムの比較グラフを作成する

        Args:
            summary: サマリーデータ
            save_path: 保存先パス

        Returns:
            保存したファイルパス
        """
        if save_path is None:
            save_path = self.output_dir / "response_time_comparison.png"
        else:
            save_path = Path(save_path)

        models = summary['models']
        model_names = list(models.keys())

        # データの準備
        response_times = [models[m]['avg_response_time'] for m in model_names]

        # グラフの作成
        fig, ax = plt.subplots(figsize=(10, 6))

        bars = ax.barh(model_names, response_times, color=self.colors[:len(model_names)])
        ax.set_xlabel('Average Response Time (seconds)', fontsize=12)
        ax.set_ylabel('Model', fontsize=12)
        ax.set_title('Average Response Time by Model', fontsize=14, fontweight='bold')

        # 値をバーの横に表示
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{width:.2f}s',
                   ha='left', va='center', fontsize=10, fontweight='bold')

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"レスポンスタイム比較グラフ保存: {save_path}")
        return str(save_path)

    def plot_radar_chart(
        self,
        summary: Dict,
        save_path: Optional[str] = None
    ) -> str:
        """
        各モデルの総合評価レーダーチャートを作成する

        Args:
            summary: サマリーデータ
            save_path: 保存先パス

        Returns:
            保存したファイルパス
        """
        if save_path is None:
            save_path = self.output_dir / "radar_chart.png"
        else:
            save_path = Path(save_path)

        models = summary['models']
        model_names = list(models.keys())

        # 評価項目
        categories = ['Field Accuracy', 'F1 Score', 'Exact Match', 'Schema Conf.', 'Cost Eff.']
        num_vars = len(categories)

        # 各モデルのデータを準備
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

        # 角度を計算
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]  # 閉じるために最初の角度を追加

        for i, model_name in enumerate(model_names):
            model_data = models[model_name]

            # コスト効率は逆転（低いほど良い）、正規化
            max_cost = max([models[m]['avg_cost_per_pdf'] for m in model_names])
            cost_efficiency = 1 - (model_data['avg_cost_per_pdf'] / max_cost) if max_cost > 0 else 1

            values = [
                model_data['avg_field_accuracy'],
                model_data['avg_f1_score'],
                model_data['exact_match_rate'],
                model_data['schema_conformance_rate'],
                cost_efficiency
            ]
            values += values[:1]  # 閉じるために最初の値を追加

            ax.plot(angles, values, 'o-', linewidth=2, label=model_name, color=self.colors[i])
            ax.fill(angles, values, alpha=0.15, color=self.colors[i])

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11)
        ax.set_ylim(0, 1)
        ax.set_title('Model Performance Radar Chart', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax.grid(True)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"レーダーチャート保存: {save_path}")
        return str(save_path)

    def plot_detailed_metrics(
        self,
        df: pd.DataFrame,
        save_path: Optional[str] = None
    ) -> str:
        """
        詳細メトリクスのヒートマップを作成する

        Args:
            df: メトリクスのDataFrame
            save_path: 保存先パス

        Returns:
            保存したファイルパス
        """
        if save_path is None:
            save_path = self.output_dir / "detailed_metrics_heatmap.png"
        else:
            save_path = Path(save_path)

        # モデル×PDFのピボットテーブル作成
        pivot = df.pivot_table(
            values='field_accuracy',
            index='pdf_name',
            columns='model',
            aggfunc='mean'
        )

        # グラフの作成
        fig, ax = plt.subplots(figsize=(12, max(8, len(pivot) * 0.5)))

        sns.heatmap(pivot, annot=True, fmt='.2f', cmap='RdYlGn',
                   vmin=0, vmax=1, linewidths=0.5,
                   cbar_kws={'label': 'Field Accuracy'},
                   ax=ax)

        ax.set_title('Field Accuracy Heatmap (Model × PDF)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Model', fontsize=12)
        ax.set_ylabel('PDF', fontsize=12)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"詳細メトリクスヒートマップ保存: {save_path}")
        return str(save_path)

    def plot_cost_breakdown(
        self,
        summary: Dict,
        save_path: Optional[str] = None
    ) -> str:
        """
        コスト内訳の積み上げ棒グラフを作成する

        Args:
            summary: サマリーデータ
            save_path: 保存先パス

        Returns:
            保存したファイルパス
        """
        if save_path is None:
            save_path = self.output_dir / "cost_breakdown.png"
        else:
            save_path = Path(save_path)

        models = summary['models']
        model_names = list(models.keys())

        # データの準備
        total_costs = [models[m]['total_cost'] for m in model_names]
        counts = [models[m]['count'] for m in model_names]

        # グラフの作成
        fig, ax = plt.subplots(figsize=(10, 6))

        bars = ax.bar(model_names, total_costs, color=self.colors[:len(model_names)])
        ax.set_xlabel('Model', fontsize=12)
        ax.set_ylabel('Total Cost (JPY)', fontsize=12)
        ax.set_title('Total Cost by Model', fontsize=14, fontweight='bold')
        ax.tick_params(axis='x', rotation=45)

        # 値とPDF数をバーの上に表示
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'¥{height:.0f}\n({counts[i]} PDFs)',
                   ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"コスト内訳グラフ保存: {save_path}")
        return str(save_path)

    def plot_token_usage(
        self,
        summary: Dict,
        save_path: Optional[str] = None
    ) -> str:
        """
        トークン使用量のグラフを作成する

        Args:
            summary: サマリーデータ
            save_path: 保存先パス

        Returns:
            保存したファイルパス
        """
        if save_path is None:
            save_path = self.output_dir / "token_usage.png"
        else:
            save_path = Path(save_path)

        models = summary['models']
        model_names = list(models.keys())

        # データの準備
        total_tokens = [models[m]['total_tokens'] for m in model_names]

        # グラフの作成
        fig, ax = plt.subplots(figsize=(10, 6))

        bars = ax.bar(model_names, total_tokens, color=self.colors[:len(model_names)])
        ax.set_xlabel('Model', fontsize=12)
        ax.set_ylabel('Total Tokens', fontsize=12)
        ax.set_title('Total Token Usage by Model', fontsize=14, fontweight='bold')
        ax.tick_params(axis='x', rotation=45)

        # 値をバーの上に表示
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:,.0f}',
                   ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()

        logger.info(f"トークン使用量グラフ保存: {save_path}")
        return str(save_path)

    def generate_all_visualizations(
        self,
        summary_path: str,
        csv_path: Optional[str] = None
    ) -> List[str]:
        """
        すべての可視化を一度に生成する

        Args:
            summary_path: サマリーファイルのパス
            csv_path: メトリクスCSVのパス（オプション）

        Returns:
            生成されたファイルパスのリスト
        """
        logger.info("すべての可視化を生成中...")

        summary = self.load_summary(summary_path)
        generated_files = []

        # 各グラフを生成
        try:
            generated_files.append(self.plot_accuracy_comparison(summary))
        except Exception as e:
            logger.error(f"精度比較グラフ生成エラー: {str(e)}")

        try:
            generated_files.append(self.plot_cost_vs_accuracy(summary))
        except Exception as e:
            logger.error(f"コスト vs 精度グラフ生成エラー: {str(e)}")

        try:
            generated_files.append(self.plot_response_time_comparison(summary))
        except Exception as e:
            logger.error(f"レスポンスタイム比較グラフ生成エラー: {str(e)}")

        try:
            generated_files.append(self.plot_radar_chart(summary))
        except Exception as e:
            logger.error(f"レーダーチャート生成エラー: {str(e)}")

        try:
            generated_files.append(self.plot_cost_breakdown(summary))
        except Exception as e:
            logger.error(f"コスト内訳グラフ生成エラー: {str(e)}")

        try:
            generated_files.append(self.plot_token_usage(summary))
        except Exception as e:
            logger.error(f"トークン使用量グラフ生成エラー: {str(e)}")

        # CSVがあれば詳細メトリクスも生成
        if csv_path:
            try:
                df = self.load_metrics_csv(csv_path)
                generated_files.append(self.plot_detailed_metrics(df))
            except Exception as e:
                logger.error(f"詳細メトリクスグラフ生成エラー: {str(e)}")

        logger.info(f"可視化生成完了: {len(generated_files)}ファイル")
        return generated_files
