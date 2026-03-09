import os
import shutil
from core.task_base import TaskBase

class RemoveBgTask(TaskBase):
    def __init__(self, config_manager):
        super().__init__("RemoveBG", "bg_remover_3 による高品質背景透過", config_manager)

    def execute(self, input_dir, output_dir, logger=None):
        if not self.is_enabled:
            if logger: logger("スキップされました (Disabled)")
            return True

        tool_path = self.config.get("tools", "bg_remover_3")
        if logger: logger(f"RemoveBgTask 開始... 入力:{input_dir} 出力:{output_dir}")
        if logger: logger(f"外部ツールパス: {tool_path}")

        try:
            os.makedirs(output_dir, exist_ok=True)
            files_processed = 0
            for filename in os.listdir(input_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    src = os.path.join(input_dir, filename)
                    # ダミー: ここで本来は透過処理される
                    dst = os.path.join(output_dir, f"nobg_{filename}")
                    shutil.copy2(src, dst)
                    files_processed += 1
            
            if logger: logger(f"RemoveBgTask 完了: {files_processed}ファイルの処理成功")
            return True
        except Exception as e:
            if logger: logger(f"RemoveBgTask エラー: {str(e)}")
            return False
