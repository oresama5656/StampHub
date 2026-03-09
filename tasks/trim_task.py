import os
import shutil
from core.task_base import TaskBase

class TrimTask(TaskBase):
    def __init__(self, config_manager):
        super().__init__("Trim", "不要な透明領域の自動クロップ", config_manager)

    def execute(self, input_dir, output_dir, logger=None):
        if not self.is_enabled:
            if logger: logger("スキップされました (Disabled)")
            return True

        if logger: logger(f"TrimTask 開始... 入力:{input_dir} 出力:{output_dir}")

        try:
            os.makedirs(output_dir, exist_ok=True)
            files_processed = 0
            for filename in os.listdir(input_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    src = os.path.join(input_dir, filename)
                    # ダミー: ここで本体はPillow等を使ってオートクロップする
                    dst = os.path.join(output_dir, f"trim_{filename}")
                    shutil.copy2(src, dst)
                    files_processed += 1
            
            if logger: logger(f"TrimTask 完了: {files_processed}ファイルの処理成功")
            return True
        except Exception as e:
            if logger: logger(f"TrimTask エラー: {str(e)}")
            return False
