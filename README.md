# StampHub 🚀

LINEスタンプ制作ワークフローを統合するハブアプリケーション。
複数の独立したツールを一本化し、高精度な背景透過、画像分割、成形を自動化します。

## 🌟 主な機能

1.  **スタンプ分割**: シート画像を個別のスタンプ画像に自動分割。
2.  **高精度AI背景透過**: `bg_remover_3` (isnet-animeモデル) と連携した高品質な透過処理。
3.  **自動トリミング**: 透明部分をカットし、最適な余白を付与。
4.  **LINEスタンプ整形**: 規定サイズ (370x320px) へのリサイズ、main/tab画像の生成。

## 🛠️ 技術スタック

-   Python 3.x
-   CustomTkinter (現代的なモダンUI)
-   OpenCV / NumPy
-   bg_remover_3 (rembg + isnet-anime) 連携

## 🚀 セットアップ

### 1. リポジトリのクローン
```bash
git clone https://github.com/[USER_NAME]/StampHub.git
cd StampHub
```

### 2. 仮想環境の構築
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 実行
```bash
python gui/main_gui.py
```

## 📂 構成
- `gui/`: アプリケーションのUI実装
- `core/`: 基盤となるタスククラス（実装予定）
- `tasks/`: 各工程の具体的なロジック
- `config.json`: 外部ツールパス等の設定管理

## 🤝 外部ツールとの連携
本ツールは以下の外部ツールと連携することを前提としています。
- `D:\stamp_maker_banana`
- `D:\bg_remover_3`

---
Developed by Antigravity
