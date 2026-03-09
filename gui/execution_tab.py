import os
import shutil
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QPushButton, QProgressBar, QScrollArea, QFrame
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Import task registry
from tasks import TASK_REGISTRY

class TaskWorker(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, tasks, config):
        super().__init__()
        self.tasks = tasks # list of dicts {"name": ..., "id": ..., "enabled": ...}
        self.config = config

    def run(self):
        self.log.emit(">>> パイプライン処理を開始します...")
        total_tasks = len([t for t in self.tasks if t['enabled']])
        if total_tasks == 0:
            self.log.emit("実行するタスクがありません。")
            self.finished.emit(True)
            return

        completed = 0
        input_dir = self.config.get("directories", "input_dir")
        temp_dir = self.config.get("directories", "temp_dir")
        output_dir = self.config.get("directories", "output_dir")

        # 実行前に一時フォルダをクリア
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)
        
        # 初期状態では input_dir から読み込む
        current_input = input_dir

        for i, task_info in enumerate(self.tasks):
            if not task_info['enabled']:
                continue
                
            task_id = task_info['id']
            task_name = task_info['name']
            self.log.emit(f"実行中: [{task_name}] ...")
            
            # タスクインスタンスの作成
            TaskClass = TASK_REGISTRY.get(task_id)
            if not TaskClass:
                self.log.emit(f"エラー: タスク '{task_id}' が見つかりません。")
                self.finished.emit(False)
                return
                
            task_instance = TaskClass(self.config)
            
            # 最後のタスク以外は一時フォルダのサブディレクトリに出力する
            is_last_task = (completed == total_tasks - 1)
            current_output = output_dir if is_last_task else os.path.join(temp_dir, f"step_{completed+1}_{task_id}")
            
            # タスク実行
            def logger_callback(msg):
                self.log.emit(msg)
                
            success = task_instance.execute(current_input, current_output, logger=logger_callback)
            
            if not success:
                self.log.emit(f"[{task_name}] でエラーが発生したため、処理を中断します。")
                self.finished.emit(False)
                return
            
            # 次のタスクの入力ディレクトリを現在の出力ディレクトリに更新
            current_input = current_output
            
            completed += 1
            progress_val = int((completed / total_tasks) * 100)
            self.progress.emit(progress_val)

        self.log.emit(">>> 全ての処理が完了しました！出力フォルダを確認してください。")
        self.finished.emit(True)


class ExecutionTab(QWidget):
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        # 将来的にtasksディレクトリを動的スキャンしてここに追加する形になります。
        self.available_tasks = [
            {"id": "split", "name": "1. Split (画像分割)", "desc": "stamp_maker_banana による画像分割処理"},
            {"id": "remove_bg", "name": "2. RemoveBG (高品質背景透過)", "desc": "bg_remover_3 による透過処理"},
            {"id": "trim", "name": "3. Trim (自動余白カット)", "desc": "不要な透明領域の自動クロップ"},
            {"id": "format", "name": "4. Format (規定サイズ成形)", "desc": "LINEスタンプ規定サイズへリサイズ＆センタリング"}
        ]
        self.task_checkboxes = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("実行パイプライン構成")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        layout.addWidget(title)

        # Scroll area for tasks
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: 1px solid #eee; border-radius: 8px; background-color: #fafafa; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        tasks_layout = QVBoxLayout(scroll_content)
        tasks_layout.setSpacing(10)
        tasks_layout.setAlignment(Qt.AlignTop)

        # Create task toggles
        for task in self.available_tasks:
            task_widget = self.create_task_widget(task)
            tasks_layout.addWidget(task_widget)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, 1) # stretch factor 1

        # Control area (Progress and Run buttons)
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        control_layout = QVBoxLayout(control_frame)
        control_layout.setContentsMargins(20, 20, 20, 20)

        # Log label
        self.status_label = QLabel("待機中...")
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        control_layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #06C755;
                border-radius: 5px;
            }
        """)
        control_layout.addWidget(self.progress_bar)

        # Spacer
        control_layout.addSpacing(10)

        # Run Button
        self.run_btn = QPushButton("🚀 パイプラインを実行")
        self.run_btn.setFixedHeight(50)
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #06C755;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover { background-color: #05B34C; }
            QPushButton:disabled { background-color: #a0a0a0; }
        """)
        self.run_btn.clicked.connect(self.run_pipeline)
        control_layout.addWidget(self.run_btn)

        layout.addWidget(control_frame)
        self.setLayout(layout)

    def create_task_widget(self, task_info):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #ddd;
            }
            QFrame:hover { border: 1px solid #06C755; }
        """)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)

        # Checkbox for toggle
        checkbox = QCheckBox(task_info["name"])
        checkbox.setChecked(True) # Default all on
        checkbox.setStyleSheet("""
            QCheckBox { font-size: 14px; font-weight: bold; }
            QCheckBox::indicator { width: 40px; height: 20px; }
            /* Styling for toggle switch can be complex in generic QSS, keeping simple checkbox for now but oversized */
        """)
        self.task_checkboxes.append({"info": task_info, "checkbox": checkbox})
        
        # Description
        desc = QLabel(task_info["desc"])
        desc.setStyleSheet("color: #777; font-size: 12px;")
        
        info_layout = QVBoxLayout()
        info_layout.addWidget(checkbox)
        info_layout.addWidget(desc)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        return frame

    def run_pipeline(self):
        # Gather enabled tasks
        active_tasks = []
        for item in self.task_checkboxes:
            active_tasks.append({
                "name": item["info"]["name"],
                "id": item["info"]["id"],
                "enabled": item["checkbox"].isChecked()
            })

        self.run_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("処理を開始しています...")

        # Run in worker thread to prevent GUI freezing
        self.worker = TaskWorker(active_tasks, self.config_manager)
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.update_log)
        self.worker.finished.connect(self.pipeline_finished)
        self.worker.start()

    def update_progress(self, val):
        self.progress_bar.setValue(val)

    def update_log(self, text):
        self.status_label.setText(text)

    def pipeline_finished(self, success):
        self.run_btn.setEnabled(True)
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText("処理が完了しました。出力フォルダを確認してください。")
