from google.cloud import bigquery
import pandas as pd
import os
import time

def get_dataframe():
    """BigQueryからデータを読み込んで返す"""
    # サービスアカウントキーのパスを設定
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'sunnyrex-mura-461103-ceaab7b20ed1.json'

    # BigQueryクライアント初期化
    client = bigquery.Client(project="sunnyrex-mura-461103")

    # テーブルID
    table_id = "sunnyrex-mura-461103.CMdata.new"

    # BigQueryからPandasに読み込む（BigQuery Storage APIを使用）
    print("BigQueryからデータを読み込み中...")
    start_time = time.time()
    df = client.list_rows(table_id).to_dataframe(create_bqstorage_client=True)
    elapsed_time = time.time() - start_time

    # 読み込み完了情報
    print(f"[OK] 読み込み完了！ ({elapsed_time:.1f}秒)")
    print(f"  - 行数: {len(df):,}")
    print(f"  - 列数: {len(df.columns)}")
    print(f"\nデータサイズ: {df.memory_usage(deep=True).sum() / (1024**2):.2f} MB")

    return df

if __name__ == '__main__':
    df = get_dataframe()
    print(f"\nカラム一覧:")
    print(df.columns.tolist())
    print(f"\n最初の5行:")
    print(df.head())
