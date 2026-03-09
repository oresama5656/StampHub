import codecs
import os

with codecs.open(r"D:\stamp_maker_banana\gui.py", "r", "utf-8") as f:
    code = f.read()

# 1. Insert sys.path.append before import tool functions
import_target = "# Import tool functions\n"
new_import = """import sys
import os
sys.path.append(r"D:\\stamp_maker_banana")
# Import tool functions
"""
code = code.replace(import_target, new_import)

# 2. Update Window title
code = code.replace('self.title("LINE Stamp Maker Banana")', 'self.title("StampHub (Banana Layout + bg_remover_3)")')

# 3. Replace Step 2 logic
step2_target = """            # 2. BG Remove
            if self.check_bg_var.get():
                output_bg = os.path.join(final_output_dir, "temp_bg")
                if os.path.exists(output_bg): shutil.rmtree(output_bg)
                
                print("\\n[Step 2] 背景を透過中...")
                process_remover(
                    current_input, 
                    output_bg, 
                    mode=self.mode_var.get(), 
                    tolerance=int(self.tol_slider.get()),
                    erosion=int(self.bg_ero_slider.get())
                )
                current_input = output_bg"""

new_step2 = """            # 2. BG Remove (bg_remover_3 wrapper)
            if self.check_bg_var.get():
                output_bg = os.path.join(final_output_dir, "temp_bg")
                if os.path.exists(output_bg): shutil.rmtree(output_bg)
                
                print("\\n[Step 2] 背景を透過中... (bg_remover_3連携)")
                import subprocess
                bg_script = r"D:\\bg_remover_3\\bg_remover.py"
                cmd = [sys.executable, bg_script, "-i", current_input, "-o", output_bg]
                
                mode_val = self.mode_var.get()
                tol_val = int(self.tol_slider.get())
                ero_val = int(self.bg_ero_slider.get())
                
                if mode_val in ["color", "auto_color"]:
                    cmd.extend(["-c", "auto"])
                    cmd.extend(["--color-tolerance", str(tol_val)])
                    if ero_val > 0:
                        cmd.extend(["--color-erode", str(ero_val)])
                else:
                    # mode == flood or disabled, use pure AI removal
                    pass
                
                print(f"コマンド実行: {' '.join(cmd)}")
                
                # subprocessを実行し、出力を逐次ログ画面に表示する
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
                for line in process.stdout:
                    print(line, end='')
                process.wait()
                
                if process.returncode != 0:
                    print(f"\\n背景透過処理でエラーが発生しました (終了コード: {process.returncode})")
                    
                current_input = output_bg"""

code = code.replace(step2_target, new_step2)

with codecs.open(r"D:\StampHub\gui\main_gui.py", "w", "utf-8") as f:
    f.write(code)
print("Migration complete!")
