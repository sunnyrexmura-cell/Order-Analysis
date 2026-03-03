"""
フィルタ機能モジュール
発送日、店舗名、配送便、仕入先名のフィルタUI
"""

import pandas as pd
import streamlit as st


def apply_date_filter(df_data, filter_opts):
    """発送日フィルタの適用"""
    if 'min_date' not in filter_opts:
        return df_data

    date_range = st.sidebar.date_input(
        "📅 発送日（期間）",
        value=(filter_opts['min_date'], filter_opts['max_date']),
        min_value=filter_opts['min_date'],
        max_value=filter_opts['max_date']
    )

    if len(date_range) == 2:
        # 既に日付型なら直接比較（高速）
        mask = (df_data['日付'] >= date_range[0]) & (df_data['日付'] <= date_range[1])
        return df_data[mask]

    return df_data


def apply_checkbox_filter(df_data, filter_key, display_name, icon, column_name, filter_opts):
    """チェックボックス形式フィルタの適用（店舗名、配送便、仕入先名）"""
    df_filtered = df_data

    if filter_key in filter_opts:
        options = filter_opts[filter_key]

        # セッション状態の初期化（expander外で行う）
        for option in options:
            session_key = f"{filter_key}_{option}"
            if session_key not in st.session_state:
                st.session_state[session_key] = True

        with st.sidebar.expander(f"{icon} {display_name}", expanded=False):
            # ボタン行
            col_select, col_clear = st.columns([1, 1], gap="small")
            with col_select:
                if st.button("全選択", key=f"btn_select_{filter_key}", use_container_width=True):
                    for option in options:
                        st.session_state[f"{filter_key}_{option}"] = True
                    st.rerun()
            with col_clear:
                if st.button("全解除", key=f"btn_clear_{filter_key}", use_container_width=True):
                    for option in options:
                        st.session_state[f"{filter_key}_{option}"] = False
                    st.rerun()

            st.divider()

            selected_options = []
            for option in options:
                session_key = f"{filter_key}_{option}"
                if st.checkbox(option, key=session_key):
                    selected_options.append(option)

        if selected_options:
            df_filtered = df_filtered[df_filtered[column_name].isin(selected_options)]

    return df_filtered


def apply_all_filters(df_data, filter_opts):
    """すべてのフィルタを適用（高速版）"""
    df_filtered = df_data

    # 発送日フィルタ
    df_filtered = apply_date_filter(df_filtered, filter_opts)

    # 店舗名フィルタ
    df_filtered = apply_checkbox_filter(df_filtered, 'stores', '店舗名', '🏪', '店舗名', filter_opts)

    # 配送便フィルタ
    df_filtered = apply_checkbox_filter(df_filtered, 'methods', '配送便', '🚚', '配送便名', filter_opts)

    # 仕入先名フィルタ
    df_filtered = apply_checkbox_filter(df_filtered, 'suppliers', '仕入先名', '🏭', '仕入先名１', filter_opts)

    return df_filtered


def show_filter_summary(df_data, df_filtered):
    """フィルタ結果の表示とCSVダウンロード"""
    st.sidebar.markdown("---")
    col1, col2, col3 = st.sidebar.columns([1, 1, 1])
    with col1:
        st.markdown(f"**{len(df_filtered):,}**")
    with col2:
        st.markdown(f"**/ {len(df_data):,}**")
    with col3:
        # CSVデータを生成
        csv_data = df_filtered.to_csv(index=False, encoding='utf-8-sig')

        st.download_button(
            label="📥 CSV",
            data=csv_data,
            file_name=f"filtered_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
