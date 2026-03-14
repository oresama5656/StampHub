# StampHub 🚀 - Premium Stamp Production Hub

LINEスタンプ制作におけるすべての工程を一本化する、高機能ワークフロー統合ハブです。
バラバラだった「分割」「透過」「生成」「整理」「投稿」のツールを統合し、圧倒的な効率化を実現します。

## 🌟 主な機能

### 🎨 スタンプ制作 (Creation)
- **自動分割・透過・整形**: Banana Makerのロジックを引き継ぎ、1工程でLINE規定サイズまで一気に仕上げます。
- **高精度AI背景透過**: `bg_remover_3` (isnet-animeモデル) との密な連携により、髪の毛などの微細なエッジも綺麗に透過。
- **リネーム・ZIP生成**: 01.png〜40.pngへの一括リネーム、および投稿用ZIPの自動パッキング。

### 📂 管理・整理 (Management & Organization)
- **ストレージ・モニタリング**: `WorkBench`, `Ready`, `Archive` など、各フェーズのフォルダ容量をリアルタイム監視。容量が増えると警告色でお知らせ。
- **自動仕分け (Sorting)**: 
    - **製造完了**: できたてのZIPを投稿待ちへ、中間ファイルを履歴へワンクリックで自動移動。
    - **投稿完了**: 無事に投稿し終えたZIPをアーカイブフォルダへ片付け。

### 📁 AI & フォルダ (AI & Folder Operations)
- **テーマ別一括作成**: CSVからテーマ名を読み取り、`assets/images` 内に制作依頼用フォルダを自動一括生成。
- **プロンプト統合**: 別々のプロンプトCSVを一つのファイルにマージ。

### 🤖 連携ツール (External Tool Integration)
- **AutoPrompter**: ChatGPT等で使用するスタンプ案生成プロンプトツール。
- **Uploader**: 完成したZIPをLINE公式のマイページへ自動アップロード。
- **専用コンソール起動**: 外部ツールを起動する際、独自の専用ウィンドウを立ち上げるため、ログの確認や操作もスムーズ。

## 🛠️ 技術スタック

- **Python 3.x**
- **CustomTkinter**: 現代的なモダンUI（LINEグリーンを基調としたプレミアムデザイン）
- **OpenCV / NumPy**: 高速な画像処理
- **bg_remover_3**: AIモデルによる高品質背景透過
- **Smart Sorting Engine**: タイムスタンプによる衝突回避機能を備えたファイル整理システム

## 🚀 セットアップ

### 1. 仮想環境の構築
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 実行
```bash
python gui/main_gui.py
```

### 3. 初期設定
起動後、「⚙️ 設定」タブにて以下のパスを指定してください：
- `workspace_dir`: 作業場 (WorkBench) の場所
- 各ツールの実行ファイル (`.py` または `.bat`) の場所

## 📂 プロジェクト構成

- `gui/`: デザインとUI制御 (main_gui.py, styles.py)
- `core/`: 基盤システム (config_manager.py, tasks.py)
- `tasks/`: 画像処理、ファイル操作の個別タスク
- `assets/`: 画像データ、プロンプト、CSV格納用（Git管理外の重いデータ）
- `config.json`: ユーザーごとの詳細な設定管理

---
Developed by **Antigravity**
Premium Stamp Production Solution for Professional Creators
