from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QGroupBox, QScrollArea, QFormLayout
from PyQt5.QtCore import Qt

class SettingsTab(QWidget):
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        # 1. 外部ツール設定
        self.create_tools_section()

        # 2. フォルダ設定
        self.create_directories_section()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # 保存ボタン
        save_btn = QPushButton("設定を保存")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #06C755;
                color: white;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #05B34C; }
        """)
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def create_tools_section(self):
        group = QGroupBox("🛠️ 外部ツール連携パス")
        group.setStyleSheet("QGroupBox { font-size: 14px; font-weight: bold; }")
        layout = QFormLayout()
        layout.setSpacing(15)
        
        self.tool_inputs = {}
        tools_config = self.config_manager.get("tools")
        
        for tool_name, tool_path in tools_config.items():
            row_layout = QHBoxLayout()
            
            path_input = QLineEdit(tool_path)
            path_input.setStyleSheet("QLineEdit { padding: 8px; border: 1px solid #ddd; border-radius: 4px; }")
            self.tool_inputs[tool_name] = path_input
            
            browse_btn = QPushButton("参照")
            browse_btn.setStyleSheet("QPushButton { padding: 8px 15px; border-radius: 4px; background-color: #f0f0f0; }")
            browse_btn.clicked.connect(lambda checked, name=tool_name, line_edit=path_input: self.browse_file(name, line_edit))
            
            row_layout.addWidget(path_input)
            row_layout.addWidget(browse_btn)
            
            # Using simple text formatting for labels
            formatted_name = tool_name.replace("_", " ").title()
            layout.addRow(QLabel(formatted_name + ":"), row_layout)

        group.setLayout(layout)
        self.scroll_layout.addWidget(group)

    def create_directories_section(self):
        group = QGroupBox("📁 入出力ディレクトリ")
        group.setStyleSheet("QGroupBox { font-size: 14px; font-weight: bold; margin-top: 10px; }")
        layout = QFormLayout()
        layout.setSpacing(15)
        
        self.dir_inputs = {}
        dirs_config = self.config_manager.get("directories")
        
        for dir_name, dir_path in dirs_config.items():
            row_layout = QHBoxLayout()
            
            path_input = QLineEdit(dir_path)
            path_input.setStyleSheet("QLineEdit { padding: 8px; border: 1px solid #ddd; border-radius: 4px; }")
            self.dir_inputs[dir_name] = path_input
            
            browse_btn = QPushButton("参照")
            browse_btn.setStyleSheet("QPushButton { padding: 8px 15px; border-radius: 4px; background-color: #f0f0f0; }")
            browse_btn.clicked.connect(lambda checked, name=dir_name, line_edit=path_input: self.browse_directory(name, line_edit))
            
            row_layout.addWidget(path_input)
            row_layout.addWidget(browse_btn)
            
            formatted_name = dir_name.replace("_", " ").title()
            layout.addRow(QLabel(formatted_name + ":"), row_layout)

        group.setLayout(layout)
        self.scroll_layout.addWidget(group)

    def browse_file(self, tool_name, line_edit):
        file_path, _ = QFileDialog.getOpenFileName(self, f"Select {tool_name} Executable", "", "Python Files (*.py);;Executable Files (*.exe);;All Files (*)")
        if file_path:
            line_edit.setText(file_path)

    def browse_directory(self, dir_name, line_edit):
        dir_path = QFileDialog.getExistingDirectory(self, f"Select {dir_name}")
        if dir_path:
            line_edit.setText(dir_path)

    def save_settings(self):
        for tool_name, input_widget in self.tool_inputs.items():
            self.config_manager.set("tools", tool_name, input_widget.text())
            
        for dir_name, input_widget in self.dir_inputs.items():
            self.config_manager.set("directories", dir_name, input_widget.text())
            
        print("Settings saved successfully!")
