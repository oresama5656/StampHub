import os
import shutil
import subprocess
from core.task_base import TaskBase

class SplitTask(TaskBase):
    def __init__(self, config_manager):
        super().__init__("Split", "stamp_maker_banana による画像分割", config_manager)

    def execute(self, input_dir, output_dir, logger=None):
        if not self.is_enabled:
            if logger: logger("スキップされました (Disabled)")
            return True

        tool_path = self.config.get("tools", "stamp_maker_banana")
        if logger: logger(f"SplitTask 開始... 入力:{input_dir} 出力:{output_dir}")
        if logger: logger(f"外部ツールパス: {tool_path}")

        # ここで実際のツールを呼び出します（例えば subprocess.run([sys.executable, tool_path, input_dir, output_dir]) 等）
        # 今回はテスト用にファイルをコピーするダミー実装とします。
        try:
            os.makedirs(output_dir, exist_ok=True)
            files_processed = 0
            for filename in os.listdir(input_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    src = os.path.join(input_dir, filename)
                    # ダミー: ここで本来は分割されて複数のファイルになる
                    dst = os.path.join(output_dir, f"split_{filename}")
                    shutil.copy2(src, dst)
                    files_processed += 1
            
            if logger: logger(f"SplitTask 完了: {files_processed}ファイルの処理成功")
            return True
        except Exception as e:
            if logger: logger(f"SplitTask エラー: {str(e)}")
            return False
