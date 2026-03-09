import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "tools": {
        "stamp_maker_banana": "D:\\stamp_maker_banana\\main.py",
        "bg_remover_3": "D:\\bg_remover_3\\main.py"
    },
    "directories": {
        "input_dir": "D:\\StampHub\\input",
        "output_dir": "D:\\StampHub\\output",
        "temp_dir": "D:\\StampHub\\temp"
    },
    "settings": {
        "create_temp_folders_if_missing": True
    }
}

class ConfigManager:
    def __init__(self, config_path=CONFIG_FILE):
        self.config_path = config_path
        self.config = self._load_or_create()

    def _load_or_create(self):
        if not os.path.exists(self.config_path):
            self._save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                # Merge with default config to ensure all keys exist
                config = self._merge_configs(DEFAULT_CONFIG, config)
                self._save_config(config) # save the merged config back
                return config
        except json.JSONDecodeError:
            print(f"Error parsing {self.config_path}. Recreating with defaults.")
            self._save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG

    def _merge_configs(self, default, current):
        """Recursively merge defaults into current config for missing keys"""
        for key, value in default.items():
            if key not in current:
                current[key] = value
            elif isinstance(value, dict) and isinstance(current[key], dict):
                self._merge_configs(value, current[key])
        return current

    def _save_config(self, config_data):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
            
    def get(self, section, key=None):
        if key:
            return self.config.get(section, {}).get(key)
        return self.config.get(section)

    def set(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self._save_config(self.config)
