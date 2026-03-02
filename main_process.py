"""
EC販売分析ダッシュボード - メインファイル
Streamlit アプリケーション
"""

import streamlit as st
import pandas as pd
from load_csv import get_dataframe_from_csv
from utils import prepare_filter_options, format_date_jp
from filters import apply_all_filters, show_filter_summary
from analysis_tabs import (
    show_trend_tab,
    show_bestseller_tab,
    show_period_comparison_tab
)
import warnings
warnings.filterwarnings('ignore')


# ===========================
# ページ設定
# ===========================
st.set_page_config(
    page_title="EC販売分析ダッシュボード",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ===========================
# パスワード認証
# ===========================
def check_password():
    """パスワード認証チェック"""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    # パスワード入力フォーム
    st.markdown("### 🔐 パスワード認証")
    password = st.text_input("パスワードを入力してください", type="password")

    if password:
        if password == "sunnyrex":
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("❌ パスワードが違います")

    return False


if not check_password():
    st.stop()


# ===========================
# データ読込
# ===========================
@st.cache_data
def load_data():
    """CSVからデータを読み込み"""
    return get_dataframe_from_csv()


def preprocess_data(df):
    """データ前処理"""
    if 'キャンセルフラグ' in df.columns:
        df = df[df['キャンセルフラグ'] != True].copy()

    # 発送日を日付マスターとして使用
    if '発送日' in df.columns:
        df['発送日'] = pd.to_datetime(df['発送日'], errors='coerce')
        if df['発送日'].dt.tz is not None:
            df['発送日'] = df['発送日'].dt.tz_localize(None)
        df['日付'] = df['発送日'].dt.date
        df['月'] = df['発送日'].dt.to_period('M')
        df['年'] = df['発送日'].dt.year
        df['年月'] = df['発送日'].dt.strftime('%Y-%m')

    return df


def calc_kpi_display(df):
    """KPI表示用の計算"""
    from utils import calc_kpi
    sales, orders, avg_value, customers = calc_kpi(df)
    return sales, orders, avg_value, customers


# ===========================
# メイン処理開始
# ===========================
st.title("📊 EC販売分析ダッシュボード")
st.markdown("クロスモール CSV 版 - 販売トレンド・ベストセラー・予測の総合分析")

# データ読込
with st.spinner("📁 データを読み込み中..."):
    df_raw = load_data()
    df = preprocess_data(df_raw)

    # デバッグ: 件数確認
    if len(df_raw) != len(df):
        st.sidebar.info(f"⚠️ 前処理で {len(df_raw) - len(df)} 件が除外されました")

# フィルタ処理
st.sidebar.markdown("## 🔍 フィルタ条件")
filter_opts = prepare_filter_options(df)
df_filtered = apply_all_filters(df, filter_opts)

# KPI表示
col1, col2, col3, col4 = st.columns(4)
sales, orders, avg_value, customers = calc_kpi_display(df_filtered)

with col1:
    st.metric("💰 総売上", f"¥{sales:,.0f}")
with col2:
    st.metric("📦 注文数", f"{orders:,}")
with col3:
    st.metric("💳 平均注文金額", f"¥{avg_value:,.0f}")
with col4:
    st.metric("👥 顧客数", f"{customers:,}")

st.divider()

# フィルタ結果の表示
show_filter_summary(df, df_filtered)

# タブ切り替え
tab1, tab2, tab3 = st.tabs(["📈 売上トレンド", "🏆 ベストセラー", "📊 期間比較"])

with tab1:
    show_trend_tab(df_filtered)

with tab2:
    show_bestseller_tab(df_filtered)

with tab3:
    show_period_comparison_tab(df_filtered)

# フッター
st.divider()
if '日付' in df_filtered.columns:
    min_date = df_filtered['日付'].min()
    max_date = df_filtered['日付'].max()
    min_date_jp = format_date_jp(min_date)
    max_date_jp = format_date_jp(max_date)
else:
    min_date_jp = max_date_jp = 'N/A'

st.markdown(f"""
**📅 データ情報**
- データ期間: {min_date_jp} 〜 {max_date_jp}
- 表示レコード数: {len(df_filtered):,} 件 / 全体: {len(df):,} 件
- 最終更新: {pd.Timestamp.now().strftime('%Y年%m月%d日 %H:%M:%S')}
""")
