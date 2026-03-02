import pandas as pd
import os
import gdown
from pathlib import Path

def get_dataframe_from_csv():
    """Google Drive または ローカルの CSV フォルダからデータを読み込んで結合"""

    # Google Drive フォルダ ID
    GOOGLE_DRIVE_FOLDER_ID = "1XQAzPbCo2IpwCX_exXtp4Yr8bL6fz0ek"
    LOCAL_FOLDER = Path('クロスモールCSV')

    # ローカルフォルダが存在するか確認
    if LOCAL_FOLDER.exists():
        print(f"📁 ローカルフォルダから読み込み中...")
        csv_files = list(LOCAL_FOLDER.glob('*.csv'))
    else:
        print(f"📁 Google Drive からデータをダウンロード中...")
        LOCAL_FOLDER.mkdir(exist_ok=True)

        try:
            gdown.download_folder(
                f"https://drive.google.com/drive/folders/{GOOGLE_DRIVE_FOLDER_ID}",
                output=str(LOCAL_FOLDER),
                quiet=True,
                use_cookies=False
            )
            csv_files = list(LOCAL_FOLDER.glob('*.csv'))
        except Exception as e:
            raise FileNotFoundError(f"❌ Google Drive からのダウンロードに失敗しました: {e}")

    if not csv_files:
        raise FileNotFoundError(f"❌ CSV ファイルが見つかりません: {LOCAL_FOLDER}")

    print(f"  - 見つかったファイル数: {len(csv_files)}")

    # すべての CSV を読み込んで結合
    dfs = []
    for csv_file in sorted(csv_files):
        try:
            print(f"  ✓ {csv_file.name} を読み込み中...", end='')

            # 複数のエンコーディングを試す
            encodings = ['utf-8', 'shift_jis', 'cp932', 'utf-8-sig']
            df = None
            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_file, encoding=encoding)
                    break
                except Exception:
                    continue

            if df is None:
                print(f" ❌ エラー: エンコーディングが対応していません")
                continue

            print(f" ({len(df):,} 行)")
            dfs.append(df)
        except Exception as e:
            print(f" ❌ エラー: {e}")

    if not dfs:
        raise ValueError("❌ 読み込み可能な CSV がありません")

    # すべてのデータフレームを結合
    result_df = pd.concat(dfs, ignore_index=True)

    print(f"\n[OK] 読み込み完了！")
    print(f"  - 合計行数: {len(result_df):,}")
    print(f"  - 列数: {len(result_df.columns)}")
    print(f"  - データサイズ: {result_df.memory_usage(deep=True).sum() / (1024**2):.2f} MB")

    return result_df

if __name__ == '__main__':
    df = get_dataframe_from_csv()
    print(f"\nカラム一覧:")
    print(df.columns.tolist())
    print(f"\n最初の5行:")
    print(df.head())
