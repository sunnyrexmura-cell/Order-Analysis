"""
ユーティリティ関数モジュール
KPI計算、フィルタオプション準備など
"""

import pandas as pd
import streamlit as st


@st.cache_data
def prepare_filter_options(df_data):
    """フィルタオプションを事前計算"""
    options = {}
    if '発送日' in df_data.columns:
        df_data['発送日'] = pd.to_datetime(df_data['発送日'], errors='coerce')
        options['min_date'] = df_data['発送日'].min()
        options['max_date'] = df_data['発送日'].max()
    if '店舗名' in df_data.columns:
        options['stores'] = sorted(df_data['店舗名'].dropna().unique().tolist())
    if '配送便名' in df_data.columns:
        options['methods'] = sorted(df_data['配送便名'].dropna().unique().tolist())
    if '仕入先名１' in df_data.columns:
        options['suppliers'] = sorted(df_data['仕入先名１'].dropna().unique().tolist())
    return options


def calc_kpi(df_data):
    """KPI計算（売上、注文数、平均金額、顧客数）"""
    sales = df_data['金額'].sum() if '金額' in df_data.columns else 0
    orders = df_data['注文番号'].nunique() if '注文番号' in df_data.columns else len(df_data)
    avg_value = sales / orders if orders > 0 else 0
    customers = df_data['注文者氏名'].nunique() if '注文者氏名' in df_data.columns else 0
    return sales, orders, avg_value, customers


def format_date_jp(date_obj):
    """日付を日本語フォーマット（YYYY年MM月DD日）"""
    if pd.isna(date_obj):
        return 'N/A'
    return pd.to_datetime(date_obj).strftime('%Y年%m月%d日')
