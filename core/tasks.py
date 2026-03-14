import os
import csv
import glob
import shutil
from datetime import datetime

def get_themes_from_csv(csv_path):
    """CSVからテーマ一覧を取得"""
    themes = set()
    try:
        with open(csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header: return []
            header = [h.strip() for h in header]

            if 'theme' in header:
                theme_idx = header.index('theme')
                for row in reader:
                    if len(row) > theme_idx and row[theme_idx].strip():
                        themes.add(row[theme_idx].strip())
            else:
                filename = os.path.basename(csv_path)
                theme_name = os.path.splitext(filename)[0].replace('_prompts', '')
                themes.add(theme_name)
    except Exception as e:
        print(f"CSV読み込みエラー: {e}")
    return list(themes)

def create_theme_folders(csv_path, output_base_dir):
    """テーマフォルダを作成"""
    themes = get_themes_from_csv(csv_path)
    if not themes:
        return 0, "テーマが見つかりませんでした。"
    
    os.makedirs(output_base_dir, exist_ok=True)
    created_count = 0
    for theme in themes:
        safe_theme = "".join([c for c in theme if c not in r'\/:*?"<>|'])
        folder_path = os.path.join(output_base_dir, safe_theme)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            created_count += 1
            
    return created_count, f"{len(themes)}個のテーマを検出し、{created_count}個のフォルダを作成しました。"

def merge_prompts(prompts_dir, output_file):
    """プロンプトCSVを統合"""
    merged_dir = os.path.join(prompts_dir, 'merged')
    csv_files = sorted(glob.glob(os.path.join(prompts_dir, '*_prompts.csv')))
    
    if not csv_files:
        return False, "統合対象のCSV(*_prompts.csv)が見つかりません。"

    existing_rows = []
    header = ['theme', 'prompt', 'done']
    
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.reader(f)
            next(reader, None) # skip header
            for row in reader:
                if row: existing_rows.append(row)

    new_rows = []
    for filepath in csv_files:
        theme = os.path.basename(filepath).replace('_prompts.csv', '')
        with open(filepath, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if row: new_rows.append([theme, row[0], ''])
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(existing_rows)
        writer.writerows(new_rows)

    os.makedirs(merged_dir, exist_ok=True)
    for filepath in csv_files:
        shutil.move(filepath, os.path.join(merged_dir, os.path.basename(filepath)))

    return True, f"統合完了: {len(new_rows)}行を追加しました。(計 {len(existing_rows)+len(new_rows)}行)"

def move_item_safe(src, dest_folder):
    """ファイルまたはフォルダを安全に移動（重複時はタイムスタンプ付与）"""
    if not os.path.exists(src):
        return False, None
    
    basename = os.path.basename(src)
    dest = os.path.join(dest_folder, basename)
    
    if os.path.exists(dest):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(basename)
        dest = os.path.join(dest_folder, f"{name}_{timestamp}{ext}")
        
    try:
        shutil.move(src, dest)
        return True, os.path.basename(dest)
    except Exception as e:
        return False, str(e)

def organize_workbench(workbench_dir, ready_dir, archive_dir):
    """WorkBenchの仕分け処理"""
    os.makedirs(ready_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)
    
    zip_count = 0
    folder_count = 0
    logs = []
    
    for item_name in os.listdir(workbench_dir):
        item_path = os.path.join(workbench_dir, item_name)
        if item_name.lower().endswith('.zip'):
            success, new_name = move_item_safe(item_path, ready_dir)
            if success:
                logs.append(f"ZIP移動: {item_name} -> {new_name}")
                zip_count += 1
        elif os.path.isdir(item_path):
            success, new_name = move_item_safe(item_path, archive_dir)
            if success:
                logs.append(f"フォルダ移動: {item_name} -> {new_name}")
                folder_count += 1
                
    return zip_count, folder_count, logs

def archive_uploaded(ready_dir, arc_zip_dir):
    """投稿済みファイルの片付け処理"""
    os.makedirs(arc_zip_dir, exist_ok=True)
    
    zip_count = 0
    logs = []
    
    if not os.path.exists(ready_dir):
        return 0, ["投稿待ちフォルダが見つかりません。"]

    for item_name in os.listdir(ready_dir):
        item_path = os.path.join(ready_dir, item_name)
        if item_name.lower().endswith('.zip'):
            success, new_name = move_item_safe(item_path, arc_zip_dir)
            if success:
                logs.append(f"ZIPアーカイブ: {item_name} -> {new_name}")
                zip_count += 1
                
    return zip_count, logs

def get_folder_size_formatted(path):
    """フォルダの合計サイズを計算して読みやすい形式で返す"""
    if not os.path.exists(path):
        return "0 B", 0, "B"
    
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
    except Exception:
        return "---", 0, "B"
    
    # 単位の変換
    raw_size = total_size
    formatted = "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if total_size < 1024.0:
            formatted = f"{total_size:.1f} {unit}"
            return formatted, raw_size, unit
        total_size /= 1024.0
    return f"{total_size:.1f} PB", raw_size, "PB"
