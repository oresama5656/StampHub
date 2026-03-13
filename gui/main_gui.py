import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import threading
import sys
import shutil
from datetime import datetime

# Import tool functions
import sys
import os
import subprocess

# プロジェクトのルートディレクトリを検索パスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

sys.path.append(r"D:\stamp_maker_banana")

from stamp_splitter_v2 import process_splitter
# from background_remover import process_remover  # Replacing with bg_remover_3
from auto_trimmer import process_auto_trimmer
from line_stamp_formatter import process_formatter

from core.config_manager import ConfigManager
from core.tasks import create_theme_folders, merge_prompts

# Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green") # LINE-like green theme

LINE_GREEN = "#06C755"
LINE_GREEN_HOVER = "#05B04C"

class RedirectText(object):
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        # メインスレッドでウィジェットを更新するようにスケジュール
        self.text_widget.after(0, self._append_text, string)

    def _append_text(self, string):
        try:
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", string)
            self.text_widget.see("end")
            self.text_widget.configure(state="disabled")
        except Exception:
            pass # ウィジェットが破棄されている場合などの対策

    def flush(self):
        pass

class StampMakerGUI(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        
        self.title("StampHub")
        self.geometry("1000x900")
        
        # Grid configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Load Configuration
        self.config_mgr = ConfigManager()
        
        self.stop_requested = False
        self.current_process = None
        
        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)
        
        self.sidebar_label = ctk.CTkLabel(self.sidebar_frame, text="StampHub", font=ctk.CTkFont(size=24, weight="bold"), text_color=LINE_GREEN)
        self.sidebar_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.btn_page_create = ctk.CTkButton(self.sidebar_frame, text="🎨 スタンプ制作", font=("Arial", 13, "bold"), anchor="w", command=lambda: self.select_page("create"), fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_page_create.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.btn_page_manage = ctk.CTkButton(self.sidebar_frame, text="📂 管理・整理", font=("Arial", 13, "bold"), anchor="w", command=lambda: self.select_page("manage"), fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_page_manage.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.btn_page_tasks = ctk.CTkButton(self.sidebar_frame, text="📁 AI & フォルダ", font=("Arial", 13, "bold"), anchor="w", command=lambda: self.select_page("tasks"), fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_page_tasks.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        self.btn_page_ai = ctk.CTkButton(self.sidebar_frame, text="🤖 連携ツール", font=("Arial", 13, "bold"), anchor="w", command=lambda: self.select_page("ai"), fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_page_ai.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        
        self.btn_page_upload = ctk.CTkButton(self.sidebar_frame, text="🚀 投稿・UP", font=("Arial", 13, "bold"), anchor="w", command=lambda: self.select_page("upload"), fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_page_upload.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

        self.btn_page_settings = ctk.CTkButton(self.sidebar_frame, text="⚙️ 設定", font=("Arial", 13, "bold"), anchor="w", command=lambda: self.select_page("settings"), fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"))
        self.btn_page_settings.grid(row=6, column=0, padx=10, pady=5, sticky="ew")

        # --- Main Content Area ---
        self.main_content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew")
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)
        
        # --- Pages ---
        self.pages = {}
        self.setup_create_page()
        self.setup_manage_page()
        self.setup_tasks_page()
        self.setup_ai_page()
        self.setup_upload_page()
        self.setup_settings_page()
        
        # Select default page
        self.select_page("create")

    def select_page(self, name):
        """表示するページを切り替える"""
        for n, page in self.pages.items():
            if n == name:
                page.grid(row=0, column=0, sticky="nsew")
                # ボタンの色を強調
                btn = getattr(self, f"btn_page_{n}")
                btn.configure(fg_color=LINE_GREEN, text_color="white")
            else:
                page.grid_forget()
                btn = getattr(self, f"btn_page_{n}")
                btn.configure(fg_color="transparent", text_color=("gray10", "gray90"))

    def setup_create_page(self):
        """スタンプ制作ページのUIを構築（既存のメインGUI）"""
        page = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent")
        self.pages["create"] = page
        
        # Grid configuration for the scrollable area
        page.grid_columnconfigure(0, weight=1)

        # --- 1. Input & Output Section ---
        self.io_frame = ctk.CTkFrame(page)
        self.io_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.io_frame.grid_columnconfigure(1, weight=1)

        # Input
        ctk.CTkLabel(self.io_frame, text="入力フォルダ:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.input_path_var = ctk.StringVar()
        self.input_entry = ctk.CTkEntry(self.io_frame, textvariable=self.input_path_var, placeholder_text="ここにフォルダをドラッグ＆ドロップ")
        self.input_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        self.input_entry.drop_target_register(DND_FILES)
        self.input_entry.dnd_bind('<<Drop>>', self.drop_input)

        self.browse_in_btn = ctk.CTkButton(self.io_frame, text="参照", width=80, command=self.browse_input)
        self.browse_in_btn.grid(row=0, column=2, padx=10, pady=5)

        # Output
        ctk.CTkLabel(self.io_frame, text="出力フォルダ:", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.output_path_var = ctk.StringVar(value=self.config_mgr.get_path("workspace_dir"))
        self.output_entry = ctk.CTkEntry(self.io_frame, textvariable=self.output_path_var, placeholder_text="出力先フォルダを選択")
        self.output_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        self.browse_out_btn = ctk.CTkButton(self.io_frame, text="参照", width=80, command=self.browse_output)
        self.browse_out_btn.grid(row=1, column=2, padx=(10, 5), pady=5)
        
        self.workbench_btn = ctk.CTkButton(
            self.io_frame, text="🛠️", width=40, font=("Arial", 16),
            fg_color="#CC7722", hover_color="#A65E16",
            command=self.set_workbench_output
        )
        self.workbench_btn.grid(row=1, column=3, padx=(0, 10), pady=5)

        # --- 2. Pipeline Options ---
        self.options_frame = ctk.CTkFrame(page)
        self.options_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.options_frame.grid_columnconfigure(1, weight=1)

        # Step 1: Split
        self.check_split_var = ctk.BooleanVar(value=True)
        self.check_split = ctk.CTkCheckBox(self.options_frame, text="1. スタンプ分割 (シート→個別)", variable=self.check_split_var, font=("Arial", 12, "bold"))
        self.check_split.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.split_opts = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.split_opts.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        ctk.CTkLabel(self.split_opts, text="分割数:").pack(side="left", padx=5)
        self.grid_var = ctk.StringVar(value="auto")
        self.grid_combo = ctk.CTkComboBox(self.split_opts, values=["auto", "4x2", "3x3", "4x4"], variable=self.grid_var, width=80)
        self.grid_combo.pack(side="left", padx=5)

        ctk.CTkLabel(self.split_opts, text="内側フチ除去:").pack(side="left", padx=(15, 5))
        self.split_margin_var = ctk.StringVar(value="0")
        self.split_margin_entry = ctk.CTkEntry(self.split_opts, textvariable=self.split_margin_var, width=40)
        self.split_margin_entry.pack(side="left", padx=5)
        ctk.CTkLabel(self.split_opts, text="px").pack(side="left")

        # Step 2: BG Remove (High Precision bg_remover_3 integration)
        self.check_bg_var = ctk.BooleanVar(value=False)
        self.check_bg = ctk.CTkCheckBox(self.options_frame, text="2. 背景透過 (高精度AI)", variable=self.check_bg_var, font=("Arial", 12, "bold"))
        self.check_bg.grid(row=1, column=0, padx=10, pady=10, sticky="nw")

        self.bg_opts = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.bg_opts.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        # --- Mode Selection ---
        self.bg_mode_var = ctk.StringVar(value="AI Only")
        ctk.CTkRadioButton(self.bg_opts, text="AIのみ抽出", variable=self.bg_mode_var, value="AI Only", command=self.update_bg_ui).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ctk.CTkRadioButton(self.bg_opts, text="ハイブリッド(文字維持)", variable=self.bg_mode_var, value="Hybrid", command=self.update_bg_ui).grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        # --- Common Settings ---
        self.common_bg_frame = ctk.CTkFrame(self.bg_opts, fg_color="transparent")
        self.common_bg_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.common_bg_frame, text="フチ削り量:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.bg_erode_val_label = ctk.CTkLabel(self.common_bg_frame, text="10", width=30)
        self.bg_erode_val_label.grid(row=0, column=2, padx=5, pady=2)
        self.bg_erode_slider = ctk.CTkSlider(self.common_bg_frame, from_=0, to=30, number_of_steps=30, width=150, 
                                            command=lambda v: self.bg_erode_val_label.configure(text=str(int(v))))
        self.bg_erode_slider.set(10)
        self.bg_erode_slider.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        self.bg_fill_holes_var = ctk.BooleanVar(value=True)
        self.bg_fill_holes_check = ctk.CTkCheckBox(self.common_bg_frame, text="中抜け防止", variable=self.bg_fill_holes_var)
        self.bg_fill_holes_check.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        
        self.bg_gpu_var = ctk.BooleanVar(value=False)
        self.bg_gpu_check = ctk.CTkCheckBox(self.common_bg_frame, text="GPU加速", variable=self.bg_gpu_var)
        self.bg_gpu_check.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        # --- Hybrid Settings ---
        self.hybrid_bg_frame = ctk.CTkFrame(self.bg_opts, fg_color=("gray85", "gray25"), corner_radius=5)
        self.hybrid_bg_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.hybrid_bg_frame, text="背景色:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.bg_color_var = ctk.StringVar(value="auto")
        self.bg_color_combo = ctk.CTkComboBox(self.hybrid_bg_frame, values=["auto", "white", "black", "green", "custom"], 
                                             variable=self.bg_color_var, width=100, command=self.on_bg_color_change)
        self.bg_color_combo.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        self.bg_custom_color_btn = ctk.CTkButton(self.hybrid_bg_frame, text="🎨", width=30, command=self.pick_bg_color)
        self.bg_custom_color_btn.grid(row=0, column=2, padx=5, pady=2)
        
        ctk.CTkLabel(self.hybrid_bg_frame, text="文字フチ削り:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.bg_color_erode_label = ctk.CTkLabel(self.hybrid_bg_frame, text="2", width=30)
        self.bg_color_erode_label.grid(row=1, column=2, padx=5, pady=2)
        self.bg_color_erode_slider = ctk.CTkSlider(self.hybrid_bg_frame, from_=0, to=10, number_of_steps=10, width=150, 
                                                  command=lambda v: self.bg_color_erode_label.configure(text=str(int(v))))
        self.bg_color_erode_slider.set(2)
        self.bg_color_erode_slider.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        ctk.CTkLabel(self.hybrid_bg_frame, text="色の許容値:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.bg_color_tol_label = ctk.CTkLabel(self.hybrid_bg_frame, text="15", width=30)
        self.bg_color_tol_label.grid(row=2, column=2, padx=5, pady=2)
        self.bg_color_tol_slider = ctk.CTkSlider(self.hybrid_bg_frame, from_=0, to=100, number_of_steps=100, width=150,
                                                command=lambda v: self.bg_color_tol_label.configure(text=str(int(v))))
        self.bg_color_tol_slider.set(15)
        self.bg_color_tol_slider.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        # 初期状態の更新
        self.update_bg_ui()

        # Step 3: Trim
        self.check_trim_var = ctk.BooleanVar(value=False)
        self.check_trim = ctk.CTkCheckBox(self.options_frame, text="3. 自動トリミング (透明部分カット)", variable=self.check_trim_var, font=("Arial", 12, "bold"))
        self.check_trim.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.trim_opts = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.trim_opts.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        ctk.CTkLabel(self.trim_opts, text="余白:").pack(side="left", padx=5)
        self.pad_var = ctk.StringVar(value="10")
        self.pad_entry = ctk.CTkEntry(self.trim_opts, textvariable=self.pad_var, width=50)
        self.pad_entry.pack(side="left", padx=5)
        ctk.CTkLabel(self.trim_opts, text="px").pack(side="left")

        # Step 4: Format
        self.check_fmt_var = ctk.BooleanVar(value=True)
        self.check_fmt = ctk.CTkCheckBox(self.options_frame, text="4. LINEスタンプ整形 (リサイズ・配置)", variable=self.check_fmt_var, font=("Arial", 12, "bold"))
        self.check_fmt.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        
        ctk.CTkLabel(self.options_frame, text="(370x320pxにリサイズ, main/tab画像生成)").grid(row=3, column=1, padx=10, pady=10, sticky="w")

        # Step 5: 出力名メモ（ZIPとバックアップフォルダの名前に付与）
        ctk.CTkLabel(self.options_frame, text="5. 出力名メモ", font=("Arial", 12, "bold")).grid(row=4, column=0, padx=10, pady=10, sticky="w")
        
        self.name_opts = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.name_opts.grid(row=4, column=1, padx=10, pady=10, sticky="w")
        
        self.prefix_var = ctk.StringVar(value="")
        self.prefix_entry = ctk.CTkEntry(self.name_opts, textvariable=self.prefix_var, width=180, placeholder_text="空欄時は入力フォルダ名を適用")
        self.prefix_entry.pack(side="left", padx=5)
        
        self.date_var = ctk.BooleanVar(value=True)  # デフォルトON
        self.date_check = ctk.CTkCheckBox(self.name_opts, text="日付を入れる", variable=self.date_var)
        self.date_check.pack(side="left", padx=10)

        # --- 3. Execution ---
        self.exec_frame = ctk.CTkFrame(page, fg_color="transparent")
        self.exec_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.exec_frame.grid_columnconfigure(0, weight=3)
        self.exec_frame.grid_columnconfigure(1, weight=1)

        self.run_btn = ctk.CTkButton(self.exec_frame, text="処理開始 (RUN)", font=("Arial", 16, "bold"), height=50, command=self.start_process)
        self.run_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.stop_btn = ctk.CTkButton(self.exec_frame, text="中止", font=("Arial", 16, "bold"), height=50, fg_color="#D32F2F", hover_color="#B71C1C", command=self.request_stop, state="disabled")
        self.stop_btn.grid(row=0, column=1, sticky="ew")

        # --- main/tab 再生成セクション ---
        self.maintab_frame = ctk.CTkFrame(page)
        self.maintab_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.maintab_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.maintab_frame, text="main/tab 再生成", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # 選択した画像のパス表示
        self.selected_img_var = ctk.StringVar(value="画像を選択してください")
        self.selected_img_label = ctk.CTkLabel(self.maintab_frame, textvariable=self.selected_img_var, anchor="w")
        self.selected_img_label.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # 画像選択ボタン
        self.select_img_btn = ctk.CTkButton(self.maintab_frame, text="画像選択", width=80, command=self.select_image_for_maintab)
        self.select_img_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # 生成ボタン
        self.gen_maintab_btn = ctk.CTkButton(self.maintab_frame, text="生成", width=60, command=self.generate_maintab)
        self.gen_maintab_btn.grid(row=0, column=3, padx=5, pady=5)

        # --- 完成後調整セクション ---
        self.finish_frame = ctk.CTkFrame(page)
        self.finish_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.finish_frame.grid_columnconfigure(0, weight=1)
        
        # セクションヘッダー
        ctk.CTkLabel(self.finish_frame, text="🎨 完成後調整", font=("Arial", 13, "bold")).grid(row=0, column=0, padx=10, pady=(8, 4), sticky="w")
        
        # --- 行1: 確認＆リネーム ---
        self.finish_row1 = ctk.CTkFrame(self.finish_frame, fg_color="transparent")
        self.finish_row1.grid(row=1, column=0, padx=10, pady=2, sticky="ew")
        
        self.open_folder_btn = ctk.CTkButton(self.finish_row1, text="📂 出力フォルダを開く", width=160, command=self.open_output_folder)
        self.open_folder_btn.pack(side="left", padx=(0, 8), pady=4)
        
        self.rename_btn = ctk.CTkButton(self.finish_row1, text="🔢 リネーム", width=100, command=self.rename_files, fg_color="#2E7D32", hover_color="#388E3C")
        self.rename_btn.pack(side="left", padx=4, pady=4)
        
        # ファイル数カウント表示エリア
        self.count_area = ctk.CTkFrame(self.finish_row1, fg_color=("gray85", "gray20"), corner_radius=8)
        self.count_area.pack(side="left", padx=8, pady=4)
        
        self.file_count_label = ctk.CTkLabel(self.count_area, text="📁 --個", font=("Arial", 13, "bold"), width=80)
        self.file_count_label.pack(side="left", padx=(10, 4), pady=4)
        
        self.refresh_count_btn = ctk.CTkButton(self.count_area, text="🔄", width=32, height=28, command=self.update_file_count, fg_color="transparent", hover_color=("gray75", "gray30"), text_color=("gray20", "gray90"))
        self.refresh_count_btn.pack(side="left", padx=(0, 6), pady=4)
        
        # --- 行2: 出力＆クリーンアップ ---
        self.finish_row2 = ctk.CTkFrame(self.finish_frame, fg_color="transparent")
        self.finish_row2.grid(row=2, column=0, padx=10, pady=(2, 8), sticky="ew")
        
        self.create_zip_btn = ctk.CTkButton(self.finish_row2, text="📦 ZIPファイル作成", width=160, command=self.create_zip)
        self.create_zip_btn.pack(side="left", padx=(0, 8), pady=4)
        
        self.delete_watermark_btn = ctk.CTkButton(self.finish_row2, text="🍌💣", width=60, command=self.delete_watermark_files)
        self.delete_watermark_btn.pack(side="left", padx=4, pady=4)
        
        self.delete_input_btn = ctk.CTkButton(self.finish_row2, text="🗑️ 入力画像クリア", width=140, command=self.delete_input_images, fg_color="#8B0000", hover_color="#B22222")
        self.delete_input_btn.pack(side="left", padx=4, pady=4)

        # --- 4. Log Area ---
        self.log_frame = ctk.CTkFrame(page)
        self.log_frame.grid(row=5, column=0, padx=20, pady=10, sticky="nsew")
        self.log_frame.grid_rowconfigure(0, weight=1)
        self.log_frame.grid_columnconfigure(0, weight=1)
        
        self.log_text = ctk.CTkTextbox(self.log_frame, state="disabled", font=("Consolas", 10), height=200)
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Redirect stdout and stderr
        sys.stdout = RedirectText(self.log_text)
        sys.stderr = RedirectText(self.log_text)

    def setup_tasks_page(self):
        """AI連携 & フォルダ一括作成ページのUI"""
        page = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.pages["tasks"] = page
        page.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(page, text="📁 AI連携 & フォルダ一括操作", font=("Arial", 20, "bold")).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Merge Section
        card1 = ctk.CTkFrame(page)
        card1.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        ctk.CTkLabel(card1, text="1. プロンプトCSV統合 (merge_prompts)", font=("Arial", 13, "bold")).pack(padx=10, pady=5, anchor="w")
        ctk.CTkLabel(card1, text="outputs/prompts/ 内の個別CSVを一つにまとめます。", font=("Arial", 11)).pack(padx=10, pady=(0, 10), anchor="w")
        
        btn_row1 = ctk.CTkFrame(card1, fg_color="transparent")
        btn_row1.pack(padx=20, pady=10, fill="x")
        ctk.CTkButton(btn_row1, text="統合を実行", command=self.exec_merge_prompts).pack(side="left", padx=5)
        ctk.CTkButton(btn_row1, text="📂 フォルダを開く", fg_color="gray30", hover_color="gray40", command=lambda: self._open_folder(r"D:\sticker-project\outputs\prompts")).pack(side="left", padx=5)

        # Create Folders Section
        card2 = ctk.CTkFrame(page)
        card2.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        ctk.CTkLabel(card2, text="2. テーマフォルダ一括作成 (create_theme_folders)", font=("Arial", 13, "bold")).pack(padx=10, pady=5, anchor="w")
        ctk.CTkLabel(card2, text="CSVに記載されたテーマ名のフォルダを images/ 内に作成します。", font=("Arial", 11)).pack(padx=10, pady=(0, 10), anchor="w")
        
        btn_row2 = ctk.CTkFrame(card2, fg_color="transparent")
        btn_row2.pack(padx=20, pady=10, fill="x")
        ctk.CTkButton(btn_row2, text="フォルダ作成を実行", command=self.exec_create_folders).pack(side="left", padx=5)
        ctk.CTkButton(btn_row2, text="📂 フォルダを開く", fg_color="gray30", hover_color="gray40", command=lambda: self._open_folder(r"D:\sticker-project\outputs\images")).pack(side="left", padx=5)

    def exec_merge_prompts(self):
        prompts_dir = r"D:\sticker-project\outputs\prompts"
        output_file = r"D:\sticker-project\outputs\all_prompts.csv"
        success, msg = merge_prompts(prompts_dir, output_file)
        print(f"\n[AIタスク] {msg}")

    def exec_create_folders(self):
        csv_path = ctk.filedialog.askopenfilename(title="テーマを読み取るCSVを選択", filetypes=[("CSV files", "*.csv")])
        if csv_path:
            output_dir = r"D:\sticker-project\outputs\images"
            count, msg = create_theme_folders(csv_path, output_dir)
            print(f"\n[フォルダタスク] {msg}")

    def setup_settings_page(self):
        """設定ページのUIを構築"""
        page = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent")
        self.pages["settings"] = page
        page.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(page, text="⚙️ システム設定", font=("Arial", 20, "bold")).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        self.path_entries = {}
        
        path_configs = [
            ("workspace_dir", "作業用フォルダ (WorkBench)"),
            ("bg_remover_py", "背景透過ツール (bg_remover.py)"),
            ("bg_remover_python", "背景透過用 Python (.venv/python.exe)"),
            ("folder_sorter_py", "管理用ツール (folder_sorter.py)"),
            ("autoprompter_bat", "AIプロンプト (AutoPrompter bat)"),
            ("uploader_bat", "アップローダー (run.bat)")
        ]
        
        for i, (key, label) in enumerate(path_configs, start=1):
            frame = ctk.CTkFrame(page)
            frame.grid(row=i, column=0, padx=20, pady=5, sticky="ew")
            frame.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(frame, text=label, width=250, anchor="w").grid(row=0, column=0, padx=10, pady=5)
            
            var = ctk.StringVar(value=self.config_mgr.get_path(key))
            entry = ctk.CTkEntry(frame, textvariable=var)
            entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
            self.path_entries[key] = var
            
            btn = ctk.CTkButton(frame, text="選択", width=60, command=lambda k=key, v=var: self.browse_path_for_setting(k, v))
            btn.grid(row=0, column=2, padx=10, pady=5)

        save_btn = ctk.CTkButton(page, text="設定を保存", height=40, font=("Arial", 14, "bold"), fg_color=LINE_GREEN, hover_color=LINE_GREEN_HOVER, command=self.save_settings)
        save_btn.grid(row=len(path_configs)+1, column=0, padx=20, pady=30, sticky="ew")

    def browse_path_for_setting(self, key, var):
        if key.endswith("_dir") or key == "workspace_dir":
            path = ctk.filedialog.askdirectory()
        else:
            path = ctk.filedialog.askopenfilename()
        if path:
            var.set(path)

    def save_settings(self):
        for key, var in self.path_entries.items():
            self.config_mgr.set_path(key, var.get())
        if self.config_mgr.save_config():
            print("\n[INFO] 設定を保存しました。")
        else:
            print("\n[ERROR] 設定の保存に失敗しました。")

    def setup_manage_page(self):
        """管理・整理ページのUIを構築（Folder Sorter統合）"""
        page = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.pages["manage"] = page
        page.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(page, text="📂 フォルダ管理・整理", font=("Arial", 20, "bold")).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        desc = "制作したスタンプを『アップロード待ち』に移動したり、完了したものを整理します。"
        ctk.CTkLabel(page, text=desc, font=("Arial", 12)).grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
        
        card = ctk.CTkFrame(page)
        card.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        card.grid_columnconfigure(0, weight=1)
        
        # Folder Sorter Actions
        btn_sorter = ctk.CTkButton(card, text="📦 製造完了（仕分け実行）", height=50, font=("Arial", 14, "bold"), fg_color="#1976D2", hover_color="#1565C0", command=self.run_folder_sorter_manufacture)
        btn_sorter.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        btn_cleanup = ctk.CTkButton(card, text="🚀 投稿完了（片付け実行）", height=50, font=("Arial", 14, "bold"), fg_color="#388E3C", hover_color="#2E7D32", command=self.run_folder_sorter_upload)
        btn_cleanup.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        note = "※ D:\\sticker-porter\\folder_sorter.py の設定に従って自動仕分けを行います。"
        ctk.CTkLabel(page, text=note, font=("Arial", 11), text_color="gray").grid(row=3, column=0, padx=20, pady=10, sticky="w")

        btn_launch = ctk.CTkButton(page, text="Folder Sorter GUIを直接開く", width=200, command=lambda: self.launch_external_tool("folder_sorter"))
        btn_launch.grid(row=4, column=0, padx=20, pady=20, sticky="w")

    def setup_ai_page(self):
        """AIプロンプトページのUIを構築（AutoPrompter統合）"""
        page = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.pages["ai"] = page
        
        ctk.CTkLabel(page, text="🤖 AIプロンプト生成", font=("Arial", 20, "bold")).pack(padx=20, pady=20, anchor="w")
        
        desc = "ChatGPT等でスタンプ案を生成するためのプロンプト管理ツールを起動します。"
        ctk.CTkLabel(page, text=desc, font=("Arial", 12)).pack(padx=20, pady=(0, 20), anchor="w")
        
        btn_launch = ctk.CTkButton(page, text="AutoPrompter 起動", height=60, width=300, font=("Arial", 16, "bold"), fg_color=LINE_GREEN, hover_color=LINE_GREEN_HOVER, command=lambda: self.launch_external_tool("autoprompter"))
        btn_launch.pack(padx=20, pady=20)

    def setup_upload_page(self):
        """投稿ページのUIを構築（Uploader統合）"""
        page = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.pages["upload"] = page
        
        ctk.CTkLabel(page, text="🚀 LINEスタンプ アップローダー", font=("Arial", 20, "bold")).pack(padx=20, pady=20, anchor="w")
        
        desc = "完成したスタンプZIPをLINE公式のマイページへ自動アップロードします。"
        ctk.CTkLabel(page, text=desc, font=("Arial", 12)).pack(padx=20, pady=(0, 20), anchor="w")
        
        btn_launch = ctk.CTkButton(page, text="Uploader 起動", height=60, width=300, font=("Arial", 16, "bold"), fg_color=LINE_GREEN, hover_color=LINE_GREEN_HOVER, command=lambda: self.launch_external_tool("uploader"))
        btn_launch.pack(padx=20, pady=20)

    def launch_external_tool(self, tool_key):
        """外部ツールを個別に起動する"""
        tools_map = {
            "folder_sorter": self.config_mgr.get_path("folder_sorter_py"),
            "autoprompter": self.config_mgr.get_path("autoprompter_bat"),
            "uploader": self.config_mgr.get_path("uploader_bat")
        }
        path = tools_map.get(tool_key)
        if not path or not os.path.exists(path):
            print(f"エラー: ツールが見つかりません。設定画面を確認してください:\n {path}")
            return
            
        print(f"ツール起動中: {os.path.basename(path)}")
        try:
            work_dir = os.path.dirname(path)
            if path.endswith(".py"):
                subprocess.Popen([sys.executable, path], cwd=work_dir)
            elif path.endswith(".bat"):
                subprocess.Popen(["cmd", "/c", path], cwd=work_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                os.startfile(path)
        except Exception as e:
            print(f"起動失敗: {e}")

    def run_folder_sorter_manufacture(self):
        """Folder Sorterの仕分け機能をバックグラウンドで実行"""
        print("\n[管理] 仕分け処理を開始します...")
        self.launch_external_tool("folder_sorter") 

    def run_folder_sorter_upload(self):
        """Folder Sorterの片付け機能をバックグラウンドで実行"""
        print("\n[管理] 片付け処理を開始します...")
        self.launch_external_tool("folder_sorter")

    def _open_folder(self, path):
        """指定したパスをエクスプローラーで開く共通メソッド"""
        if os.path.exists(path):
            subprocess.Popen(['explorer', os.path.abspath(path)])
        else:
            print(f"エラー: フォルダが見つかりません: {path}")

    def update_bg_ui(self):
        """モードに応じてUIの表示/非表示を切り替える"""
        if self.bg_mode_var.get() == "Hybrid":
            self.hybrid_bg_frame.grid()
        else:
            self.hybrid_bg_frame.grid_remove()

    def on_bg_color_change(self, value):
        if value == "custom":
            self.pick_bg_color()

    def pick_bg_color(self):
        from tkinter import colorchooser
        color = colorchooser.askcolor(title="背景色を選択")
        if color[1]: # hex
            rgb = color[0] # (r, g, b)
            self.bg_color_var.set(f"{int(rgb[0])},{int(rgb[1])},{int(rgb[2])}")

    def drop_input(self, event):
        path = event.data
        if path.startswith("{") and path.endswith("}"):
            path = path[1:-1]
        self.input_path_var.set(path)

    def browse_input(self):
        folder = ctk.filedialog.askdirectory()
        if folder:
            self.input_path_var.set(folder)

    def browse_output(self):
        folder = ctk.filedialog.askdirectory()
        if folder:
            self.output_path_var.set(folder)

    def set_workbench_output(self):
        """作業台フォルダ（設定されたworkspace）を一発で設定する"""
        workbench_path = self.config_mgr.get_path("workspace_dir")
        self.output_path_var.set(workbench_path)

    def select_image_for_maintab(self):
        """main/tab生成用の画像をファイルダイアログで選択"""
        # 出力フォルダをデフォルトの開始位置にする
        initial_dir = self.output_path_var.get()
        if not initial_dir or not os.path.exists(initial_dir):
            initial_dir = os.getcwd()
        
        file_path = ctk.filedialog.askopenfilename(
            title="main/tab生成用の画像を選択",
            initialdir=initial_dir,
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            self.selected_img_var.set(os.path.basename(file_path))
            self._selected_img_path = file_path  # フルパスを保持
            print(f"選択: {file_path}")
    
    def generate_maintab(self):
        """選択した画像からmain.pngとtab.pngを生成"""
        import cv2
        import numpy as np
        from line_stamp_formatter import resize_and_pad, resize_exact
        
        # 画像が選択されているか確認
        if not hasattr(self, '_selected_img_path') or not os.path.exists(self._selected_img_path):
            print("エラー: 画像を選択してください。")
            return
        
        # 出力フォルダを確認
        output_dir = self.output_path_var.get()
        if not output_dir or not os.path.exists(output_dir):
            print("エラー: 出力フォルダが存在しません。")
            return
        
        try:
            # 画像読み込み
            img = cv2.imdecode(np.fromfile(self._selected_img_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            if img is None:
                print("エラー: 画像を読み込めませんでした。")
                return
            
            # 4チャンネル確認
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
            elif img.shape[2] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
            
            # main.png生成 (240x240)
            main_img = resize_and_pad(img, 240, 240, margin=0)
            main_path = os.path.join(output_dir, "main.png")
            cv2.imencode(".png", main_img)[1].tofile(main_path)
            print(f"生成: {main_path}")
            
            # tab.png生成 (96x74)
            tab_img = resize_exact(img, 96, 74)
            tab_path = os.path.join(output_dir, "tab.png")
            cv2.imencode(".png", tab_img)[1].tofile(tab_path)
            print(f"生成: {tab_path}")
            
            print("main/tab 再生成完了！")
            
        except Exception as e:
            print(f"エラー: {e}")

    def open_output_folder(self):
        """出力フォルダをエクスプローラで開く"""
        import subprocess
        output_dir = self.output_path_var.get()
        
        if not output_dir or not os.path.exists(output_dir):
            print("エラー: 出力フォルダが存在しません。")
            return
        
        # Windowsでエクスプローラを開く
        subprocess.Popen(['explorer', os.path.abspath(output_dir)])
        print(f"フォルダを開きました: {os.path.abspath(output_dir)}")
        self.update_file_count()
    
    def rename_files(self):
        """出力フォルダ内のスタンプ画像を連番リネームし、個数を表示"""
        output_dir = self.output_path_var.get()
        
        if not output_dir or not os.path.exists(output_dir):
            print("エラー: 出力フォルダが存在しません。")
            return
        
        # スタンプ画像を取得（main.png, tab.png除く）
        all_files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
        stamp_files = [f for f in all_files if f.lower() not in ['main.png', 'tab.png'] and f.lower().endswith('.png')]
        stamp_files.sort()
        
        if not stamp_files:
            print("リネーム対象のスタンプ画像がありません。")
            self.update_file_count()
            return
        
        # 一時名にリネーム（衝突回避）
        temp_names = []
        for i, file in enumerate(stamp_files):
            src = os.path.join(output_dir, file)
            temp_name = f"__temp_rename_{i:04d}.png"
            dst = os.path.join(output_dir, temp_name)
            os.rename(src, dst)
            temp_names.append(temp_name)
        
        # 連番にリネーム
        for i, temp_name in enumerate(temp_names, start=1):
            src = os.path.join(output_dir, temp_name)
            new_name = f"{i:02d}.png"
            dst = os.path.join(output_dir, new_name)
            os.rename(src, dst)
        
        count = len(temp_names)
        print(f"リネーム完了: {count}個 (01.png〜{count:02d}.png)")
        self.update_file_count()
    
    def update_file_count(self):
        """出力フォルダ内のスタンプ用PNG個数をカウントしてラベルを更新"""
        output_dir = self.output_path_var.get()
        
        if not output_dir or not os.path.exists(output_dir):
            self.file_count_label.configure(text="📁 --個")
            return
        
        all_files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
        stamp_count = len([f for f in all_files if f.lower() not in ['main.png', 'tab.png'] and f.lower().endswith('.png')])
        
        self.file_count_label.configure(text=f"📁 {stamp_count}個")
    
    def create_zip(self):
        """出力フォルダをZIPファイルに圧縮（連番リネーム付き）+ フォルダも同時出力"""
        import zipfile
        from datetime import datetime
        import re
        
        output_dir = self.output_path_var.get()
        
        if not output_dir or not os.path.exists(output_dir):
            print("エラー: 出力フォルダが存在しません。")
            return
        
        # 基本名を生成
        prefix = self.prefix_var.get().strip()
        if not prefix:
            input_dir = self.input_path_var.get().strip()
            if input_dir:
                prefix = os.path.basename(os.path.normpath(input_dir))
        include_date = self.date_var.get()
        
        # 基本パーツを組み立て
        name_parts = []
        if prefix:
            name_parts.append(prefix)
        if include_date:
            name_parts.append(datetime.now().strftime("%Y%m%d"))
        
        base_name = "_".join(name_parts) if name_parts else ""
        
        # 連番を計算 (既存ZIPをチェック)
        set_num = 1
        
        while True:
            if base_name:
                full_name = f"{base_name}_Set{set_num:02d}"
            else:
                full_name = f"Set{set_num:02d}"
            
            zip_path = os.path.join(output_dir, f"{full_name}.zip")
            
            if not os.path.exists(zip_path):
                break
            set_num += 1
        
        try:
            # ファイルを取得してソート（フォルダは除外）
            all_files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
            
            # main.pngとtab.pngを分離
            special_files = [f for f in all_files if f.lower() in ['main.png', 'tab.png']]
            stamp_files = [f for f in all_files if f.lower() not in ['main.png', 'tab.png'] and f.lower().endswith('.png')]
            stamp_files.sort()  # ソート
            
            if not stamp_files and not special_files:
                print("エラー: 出力フォルダにPNG画像がありません。")
                return
            
            # ZIPファイル作成（直接連番リネームして追加）
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # スタンプ画像を連番リネームして追加
                for i, file in enumerate(stamp_files, start=1):
                    file_path = os.path.join(output_dir, file)
                    new_name = f"{i:02d}.png"  # 01.png, 02.png...
                    zipf.write(file_path, new_name)
                
                # main.pngとtab.pngはそのまま追加
                for file in special_files:
                    file_path = os.path.join(output_dir, file)
                    zipf.write(file_path, file)
            
            total_count = len(stamp_files) + len(special_files)
            print(f"\n出力完了!")
            print(f"  ZIP: {os.path.basename(zip_path)}")
            print(f"  スタンプ: {len(stamp_files)}個 (01.png〜{len(stamp_files):02d}.png にリネーム)")
            print(f"  合計: {total_count}個のファイル")
            
            # ルートのPNG画像を削除（バックアップフォルダは残す）
            deleted_count = 0
            for file in all_files:
                if file.lower().endswith('.png'):
                    file_path = os.path.join(output_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        deleted_count += 1
            
            print(f"  クリーンアップ: {deleted_count}個のルート画像を削除")
            
            # ZIPファイルの場所を開く
            import subprocess
            subprocess.Popen(['explorer', '/select,', os.path.abspath(zip_path)])
            
        except Exception as e:
            print(f"ZIP作成エラー: {e}")

    def delete_watermark_files(self):
        """9の倍数のウォーターマーク画像を削除 (09.png, 18.png, 27.png, 36.png, 45.png...)"""
        output_dir = self.output_path_var.get()
        
        if not output_dir or not os.path.exists(output_dir):
            print("エラー: 出力フォルダが存在しません。")
            return
        
        deleted_files = []
        
        # 9の倍数のファイルを検索して削除
        for i in range(9, 1000, 9):  # 9, 18, 27, 36, 45, ...
            filename = f"{i:02d}.png"
            file_path = os.path.join(output_dir, filename)
            
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    deleted_files.append(filename)
                except Exception as e:
                    print(f"削除エラー ({filename}): {e}")
        
        if deleted_files:
            print(f"🍌💣 削除完了: {', '.join(deleted_files)}")
            print(f"合計 {len(deleted_files)} 個のウォーターマーク画像を削除しました。")
        else:
            print("削除対象のウォーターマーク画像が見つかりませんでした。")

    def delete_input_images(self):
        """入力フォルダの画像ファイルのみを削除（サブフォルダやその他のファイルは残す）"""
        input_dir = self.input_path_var.get()
        
        if not input_dir or not os.path.exists(input_dir):
            print("エラー: 入力フォルダが存在しません。")
            return
        
        # 画像拡張子のリスト
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
        
        deleted_files = []
        
        for file in os.listdir(input_dir):
            file_path = os.path.join(input_dir, file)
            # ファイルのみ（フォルダは除外）、かつ画像ファイルの場合
            if os.path.isfile(file_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in image_extensions:
                    try:
                        os.remove(file_path)
                        deleted_files.append(file)
                    except Exception as e:
                        print(f"削除エラー ({file}): {e}")
        
        if deleted_files:
            print(f"入力画像クリア完了: {len(deleted_files)} 個の画像を削除しました。")
        else:
            print("削除対象の画像が見つかりませんでした。")

    def request_stop(self):
        """処理の中止をリクエストする"""
        self.stop_requested = True
        print("\n[INFO] 中止リクエストを送信しました。現在のステップ終了後に停止します...")
        if self.current_process:
            try:
                self.current_process.terminate()
                print("[INFO] 外部プロセスに終了信号を送信しました。")
            except Exception as e:
                print(f"[ERROR] プロセス終了中にエラーが発生しました: {e}")
        self.stop_btn.configure(state="disabled")

    def start_process(self):
        input_dir = self.input_path_var.get()
        output_dir = self.output_path_var.get()

        if not input_dir or not os.path.exists(input_dir):
            print("エラー: 入力フォルダを選択してください。")
            return
        
        if not output_dir:
            print("エラー: 出力フォルダを選択してください。")
            return

        self.stop_requested = False
        self.run_btn.configure(state="disabled", text="処理中...")
        self.stop_btn.configure(state="normal")
        
        # Run in thread
        thread = threading.Thread(target=self.run_pipeline, args=(input_dir, output_dir))
        thread.start()

    def run_pipeline(self, input_dir, final_output_dir):
        try:
            print(f"--- 処理開始 {datetime.now().strftime('%H:%M:%S')} ---")
            
            current_input = input_dir
            
            # 1. Split
            if self.check_split_var.get():
                output_split = os.path.join(final_output_dir, "temp_split")
                if os.path.exists(output_split): shutil.rmtree(output_split)
                
                try:
                    inner_margin = int(self.split_margin_var.get())
                except ValueError:
                    inner_margin = 0
                
                if self.stop_requested: return
                print("\n[Step 1] スタンプ画像を分割中...")
                # Splitter defaults: tolerance=50, erosion=1 (hidden from UI)
                # remove_bg=False because we have a separate BG removal step
                process_splitter(
                    current_input, 
                    output_split, 
                    tolerance=50, 
                    erosion=1, 
                    grid=self.grid_var.get(),
                    remove_bg=False,
                    inner_margin=inner_margin
                )
                current_input = output_split

            # 2. BG Remove (External Tool: bg_remover_3)
            if self.check_bg_var.get():
                if self.stop_requested: return
                output_bg = os.path.join(final_output_dir, "temp_bg")
                if os.path.exists(output_bg): shutil.rmtree(output_bg)
                
                print("\n[Step 2] 背景を透過中 (bg_remover_3 を呼び出し)...")
                
                # Build command
                bg_remover_py = self.config_mgr.get_path("bg_remover_py")
                bg_remover_venv_python = self.config_mgr.get_path("bg_remover_python")

                if not os.path.exists(bg_remover_py) or not os.path.exists(bg_remover_venv_python):
                    print(f"エラー: 背景透過ツールのパスが正しくありません。設定画面を確認してください。")
                    return
                
                cmd = [
                    bg_remover_venv_python, bg_remover_py,
                    "-i", current_input,
                    "-o", output_bg,
                    "--alpha-matting",  # Ensure border smoothing is ON
                    "--erode-size", str(int(self.bg_erode_slider.get()))
                ]
                
                if self.bg_mode_var.get() == "Hybrid":
                    cmd.extend(["-c", self.bg_color_var.get()])
                    cmd.extend(["--color-erode", str(int(self.bg_color_erode_slider.get()))])
                    cmd.extend(["--color-tolerance", str(int(self.bg_color_tol_slider.get()))])
                
                if not self.bg_fill_holes_var.get():
                    cmd.append("--no-fill-holes")
                
                if self.bg_gpu_var.get():
                    cmd.append("--gpu")
                
                # Execute external tool (Live log redirection)
                try:
                    if self.stop_requested: return
                    print(f"DEBUG: 実行コマンド: {' '.join(cmd)}")
                    
                    # 出荷時設定に合わせて -u (unbuffered) を追加して出力を確実に取得する
                    python_exe = cmd[0]
                    new_cmd = [python_exe, "-u"] + cmd[1:]
                    
                    # エンコーディング指定を確実に通すための環境変数
                    env = os.environ.copy()
                    env["PYTHONIOENCODING"] = "utf-8"
                    
                    process = subprocess.Popen(
                        new_cmd, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.STDOUT, 
                        text=True, 
                        encoding="utf-8", # bg_remover_3に合わせてutf-8を使用
                        errors="replace",
                        bufsize=1,
                        universal_newlines=True,
                        env=env
                    )
                    self.current_process = process
                    
                    # Read stdout character by character to handle progress dots etc.
                    if process.stdout:
                        while True:
                            if self.stop_requested:
                                process.terminate()
                                break
                            char = process.stdout.read(1)
                            if not char and process.poll() is not None:
                                break
                            if char:
                                print(char, end="", flush=True)
                    
                    process.wait()
                    self.current_process = None
                    
                    if self.stop_requested:
                        print("\n[INFO] 背景透過処理を中断しました。")
                        return

                    if process.returncode != 0:
                        print(f"エラー: 背景透過ツールがエラー(code {process.returncode})で終了しました。")
                        raise subprocess.CalledProcessError(process.returncode, cmd)
                        
                except Exception as e:
                    self.current_process = None
                    if not self.stop_requested:
                        print(f"実行エラー: {e}")
                        raise e
                    else:
                        print("\n[INFO] 処理が中止されました。")
                        return
                
                current_input = output_bg

            # 3. Trim
            if self.check_trim_var.get():
                if self.stop_requested: return
                output_trim = os.path.join(final_output_dir, "temp_trim")
                if os.path.exists(output_trim): shutil.rmtree(output_trim)
                
                print("\n[Step 3] 透明部分をトリミング中...")
                try:
                    padding = int(self.pad_var.get())
                except:
                    padding = 10
                
                process_auto_trimmer(current_input, output_trim, padding=padding)
                current_input = output_trim

            # 4. Format
            if self.check_fmt_var.get():
                if self.stop_requested: return
                print("\n[Step 4] LINEスタンプ形式に整形中...")
                process_formatter(current_input, final_output_dir)
                print(f"\n完了！ 出力先: {os.path.abspath(final_output_dir)}")
            else:
                if self.stop_requested: return
                print(f"\n処理完了。 最終出力: {os.path.abspath(current_input)}")

            # 一時フォルダを削除
            temp_folders = ["temp_split", "temp_bg", "temp_trim"]
            for folder in temp_folders:
                temp_path = os.path.join(final_output_dir, folder)
                if os.path.exists(temp_path):
                    shutil.rmtree(temp_path)
                    print(f"一時フォルダ削除: {folder}")
            
            # バックアップフォルダを作成（全画像をコピー）
            prefix = self.prefix_var.get().strip()
            if not prefix:
                input_dir = self.input_path_var.get().strip()
                if input_dir:
                    prefix = os.path.basename(os.path.normpath(input_dir))
            include_date = self.date_var.get()
            
            # バックアップフォルダ名を生成
            backup_parts = []
            if prefix:
                backup_parts.append(prefix)
            if include_date:
                backup_parts.append(datetime.now().strftime("%Y%m%d"))
            backup_parts.append("raw")
            
            backup_name = "_".join(backup_parts)
            backup_path = os.path.join(final_output_dir, backup_name)
            
            # 既存のバックアップフォルダがあれば連番を付ける
            if os.path.exists(backup_path):
                i = 2
                while os.path.exists(f"{backup_path}_{i}"):
                    i += 1
                backup_path = f"{backup_path}_{i}"
                backup_name = os.path.basename(backup_path)
            
            os.makedirs(backup_path, exist_ok=True)
            
            # 出力フォルダのPNG画像をバックアップにコピー
            copied_count = 0
            for file in os.listdir(final_output_dir):
                if file.lower().endswith('.png'):
                    src = os.path.join(final_output_dir, file)
                    dst = os.path.join(backup_path, file)
                    if os.path.isfile(src):
                        shutil.copy2(src, dst)
                        copied_count += 1
            
            print(f"\nバックアップ作成: {backup_name}/ ({copied_count}個の画像)")

        except Exception as e:
            print(f"\nエラーが発生しました: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.run_btn.configure(state="normal", text="処理開始 (RUN)")
            self.stop_btn.configure(state="disabled")
            if self.stop_requested:
                print("\n--- 中止 ---")
            else:
                print("\n--- 終了 ---")

if __name__ == "__main__":
    app = StampMakerGUI()
    app.mainloop()
