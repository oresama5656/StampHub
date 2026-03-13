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
