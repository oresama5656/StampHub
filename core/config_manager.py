import json
import os

class ConfigManager:
    """StampHubの設定を管理するクラス"""
    
    DEFAULT_CONFIG = {
        "paths": {
            "bg_remover_py": r"D:\bg_remover_3\bg_remover.py",
            "bg_remover_python": r"D:\bg_remover_3\.venv\Scripts\python.exe",
            "folder_sorter_py": r"D:\sticker-porter\folder_sorter.py",
            "autoprompter_bat": r"D:\LINE-\AutoPrompter\launch-chatgpt-prefix.bat",
            "uploader_bat": r"D:\line_stamp_uploader\run.bat",
            "workspace_dir": r"D:\StampHub\workspace\WorkBench"
        }
    }

    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        """config.jsonを読み込む。存在しない場合はデフォルトを作成。"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 足りないキーがあればデフォルトで補完
                    self._merge_dicts(self.DEFAULT_CONFIG, data)
                    return data
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

    def save_config(self, config_data=None):
        """設定を保存する"""
        if config_data:
            self.config = config_data
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get_path(self, key):
        """パス設定を取得"""
        return self.config.get("paths", {}).get(key, "")

    def set_path(self, key, value):
        """パス設定を更新"""
        if "paths" not in self.config:
            self.config["paths"] = {}
        self.config["paths"][key] = value

    def _merge_dicts(self, default, target):
        """再帰的に辞書をマージして不足分を補う"""
        for key, value in default.items():
            if key not in target:
                target[key] = value
            elif isinstance(value, dict) and isinstance(target[key], dict):
                self._merge_dicts(value, target[key])
