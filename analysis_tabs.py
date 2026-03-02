"""
分析タブモジュール
売上トレンド、ベストセラー、販売予測、期間比較
"""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from prophet import Prophet
from utils import calc_kpi


# キャッシュ設定
@st.cache_data
def prepare_trend_data(df_filtered):
    """トレンドデータの準備（キャッシュ）"""
    daily_sales = df_filtered.groupby('日付')['金額'].sum().reset_index()
    daily_sales.columns = ['日付', '売上']

    monthly_sales = df_filtered.groupby('年月')['金額'].sum().reset_index()
    monthly_sales.columns = ['年月', '売上']
    monthly_sales['年月'] = pd.to_datetime(monthly_sales['年月'])

    yoy_data = df_filtered.groupby(['年', '月'])['金額'].sum().reset_index()
    yoy_data['月文字列'] = yoy_data['月'].astype(str)

    return daily_sales, monthly_sales, yoy_data


@st.cache_data
def prepare_bestseller_data(df_filtered, top_n):
    """ベストセラーデータの準備（キャッシュ）"""
    bestseller = df_filtered.groupby('標準商品名').agg({
        '金額': 'sum',
        '数量': 'sum' if '数量' in df_filtered.columns else 'size'
    }).reset_index()
    bestseller.columns = ['標準商品名', '売上', '数量']
    bestseller = bestseller.sort_values('売上', ascending=False).head(top_n)
    return bestseller


def show_trend_tab(df_filtered):
    """タブ1: 売上トレンド分析"""
    st.subheader("売上トレンド分析")

    if '日付' in df_filtered.columns and '金額' in df_filtered.columns:
        # 日別売上
        daily_sales = df_filtered.groupby('日付')['金額'].sum().reset_index()
        daily_sales.columns = ['日付', '売上']

        # 月別売上
        monthly_sales = df_filtered.groupby('年月')['金額'].sum().reset_index()
        monthly_sales.columns = ['年月', '売上']
        monthly_sales['年月'] = pd.to_datetime(monthly_sales['年月'])

        # YoY比較用
        yoy_data = df_filtered.groupby(['年', '月'])['金額'].sum().reset_index()
        yoy_data['月文字列'] = yoy_data['月'].astype(str)

        # グラフ1: 日別売上
        fig_daily = go.Figure()
        fig_daily.add_trace(
            go.Scatter(x=daily_sales['日付'], y=daily_sales['売上'],
                       mode='lines', name='日別売上',
                       line=dict(color='#1f77b4', width=2),
                       fill='tozeroy', fillcolor='rgba(31, 119, 176, 0.2)',
                       hovertemplate='<b>%{x}</b><br>売上: ¥%{y:,.0f}')
        )
        fig_daily.update_layout(
            title='日別売上推移',
            xaxis_title='日付',
            yaxis_title='売上（円）',
            height=400,
            hovermode='x unified',
            template='plotly_white'
        )

        # グラフ2: 月別売上
        fig_monthly = go.Figure()
        fig_monthly.add_trace(
            go.Bar(x=monthly_sales['年月'], y=monthly_sales['売上'],
                   name='月別売上', marker=dict(color='#ff7f0e'),
                   hovertemplate='<b>%{x}</b><br>売上: ¥%{y:,.0f}')
        )
        fig_monthly.update_layout(
            title='月別売上',
            xaxis_title='月',
            yaxis_title='売上（円）',
            height=400,
            hovermode='x',
            template='plotly_white'
        )

        # グラフ3: YoY比較
        fig_yoy = go.Figure()
        for year in sorted(yoy_data['年'].unique()):
            year_data = yoy_data[yoy_data['年'] == year].sort_values('月')
            fig_yoy.add_trace(
                go.Scatter(x=year_data['月文字列'], y=year_data['金額'],
                           mode='lines+markers', name=f'{year}年',
                           line=dict(width=2), marker=dict(size=6),
                           hovertemplate='<b>%{x}</b><br>売上: ¥%{y:,.0f}')
            )
        fig_yoy.update_layout(
            title='年別比較（YoY）',
            xaxis_title='月',
            yaxis_title='売上（円）',
            height=400,
            hovermode='x unified',
            template='plotly_white'
        )

        # グラフ表示（2列）
        col_d, col_m = st.columns(2)
        with col_d:
            st.plotly_chart(fig_daily, use_container_width=True)
        with col_m:
            st.plotly_chart(fig_monthly, use_container_width=True)

        # YoY（フルサイズ）
        st.plotly_chart(fig_yoy, use_container_width=True)
    else:
        st.warning("⚠️ 売上トレンドデータが不足しています")


def show_bestseller_tab(df_filtered):
    """タブ2: ベストセラー分析"""
    st.subheader("ベストセラー分析")

    if '標準商品名' in df_filtered.columns and '金額' in df_filtered.columns:
        # フィルタ（TOP N）
        top_n = st.slider("表示件数", 5, 50, 10)

        bestseller = df_filtered.groupby('標準商品名').agg({
            '金額': 'sum',
            '数量': 'sum' if '数量' in df_filtered.columns else 'size'
        }).reset_index()
        bestseller.columns = ['標準商品名', '売上', '数量']
        bestseller = bestseller.sort_values('売上', ascending=False).head(top_n)

        fig_bestseller = go.Figure()
        fig_bestseller.add_trace(
            go.Bar(
                x=bestseller['売上'],
                y=bestseller['標準商品名'],
                orientation='h',
                marker=dict(color='#d62728'),
                text=bestseller['売上'].apply(lambda x: f'¥{x:,.0f}'),
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>売上: ¥%{x:,.0f}')
        )
        fig_bestseller.update_layout(
            title=f'ベストセラー TOP {top_n}',
            xaxis_title='売上（円）',
            yaxis_title='',
            height=600,
            showlegend=False,
            hovermode='y',
            template='plotly_white'
        )

        st.plotly_chart(fig_bestseller, use_container_width=True)

        # テーブル表示
        st.subheader("詳細データ")
        st.dataframe(bestseller, use_container_width=True)
    else:
        st.warning("⚠️ ベストセラーデータが不足しています")


def show_forecast_tab(df_filtered):
    """タブ3: 販売予測"""
    st.subheader("販売予測（Prophet）")

    if '年月' in df_filtered.columns and '金額' in df_filtered.columns:
        try:
            # 月別売上を Prophet フォーマットに
            monthly_sales = df_filtered.groupby('年月')['金額'].sum().reset_index()
            monthly_sales.columns = ['月', '売上']
            monthly_sales['月'] = pd.to_datetime(monthly_sales['月'])

            prophet_df = pd.DataFrame({
                'ds': monthly_sales['月'],
                'y': monthly_sales['売上']
            })

            # Prophet モデルの学習
            with st.spinner("🔮 予測中..."):
                model = Prophet(yearly_seasonality=True, daily_seasonality=False, interval_width=0.95)
                model.fit(prophet_df)

                # 予測期間（スライダーで選択可能）
                periods = st.slider("予測期間（ヶ月）", 1, 12, 6)

                # 将来の予測
                future = model.make_future_dataframe(periods=periods, freq='MS')
                forecast = model.predict(future)

            # グラフ作成
            fig_forecast = go.Figure()

            # 実績
            fig_forecast.add_trace(
                go.Scatter(x=prophet_df['ds'], y=prophet_df['y'],
                           mode='lines+markers', name='実績',
                           line=dict(color='#1f77b4', width=2),
                           marker=dict(size=6),
                           hovertemplate='<b>実績</b><br>%{x|%Y-%m}<br>売上: ¥%{y:,.0f}')
            )

            # 予測
            forecast_future = forecast[forecast['ds'] > prophet_df['ds'].max()]
            fig_forecast.add_trace(
                go.Scatter(x=forecast_future['ds'], y=forecast_future['yhat'],
                           mode='lines+markers', name='予測値',
                           line=dict(color='#ff7f0e', width=2, dash='dash'),
                           marker=dict(size=6),
                           hovertemplate='<b>予測</b><br>%{x|%Y-%m}<br>売上: ¥%{y:,.0f}')
            )

            # 予測区間
            fig_forecast.add_trace(
                go.Scatter(x=forecast_future['ds'].tolist() + forecast_future['ds'].tolist()[::-1],
                           y=forecast_future['yhat_upper'].tolist() + forecast_future['yhat_lower'].tolist()[::-1],
                           fill='toself', name='予測区間',
                           fillcolor='rgba(255, 127, 14, 0.2)',
                           line=dict(color='rgba(255,255,255,0)'))
            )

            fig_forecast.update_layout(
                title=f'販売予測（{periods}ヶ月先まで）',
                xaxis_title='月',
                yaxis_title='売上（円）',
                height=500,
                hovermode='x unified',
                template='plotly_white'
            )

            st.plotly_chart(fig_forecast, use_container_width=True)

            # 予測値テーブル
            st.subheader("予測詳細")
            forecast_display = forecast_future[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
            forecast_display.columns = ['日付', '予測売上', '下限', '上限']
            forecast_display['予測売上'] = forecast_display['予測売上'].apply(lambda x: f"¥{x:,.0f}")
            forecast_display['下限'] = forecast_display['下限'].apply(lambda x: f"¥{x:,.0f}")
            forecast_display['上限'] = forecast_display['上限'].apply(lambda x: f"¥{x:,.0f}")
            st.dataframe(forecast_display, use_container_width=True)

        except Exception as e:
            st.error(f"❌ 予測生成エラー: {e}")
    else:
        st.warning("⚠️ 予測に必要なデータが不足しています")


def show_period_comparison_tab(df_filtered):
    """タブ4: 期間比較"""
    st.subheader("期間比較分析")

    if '日付' in df_filtered.columns and '金額' in df_filtered.columns:
        st.write("2つの期間を選択して、売上などを比較します")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**期間1**")
            date1_start = st.date_input("開始日", value=df_filtered['日付'].min(), key="p1_start")
            date1_end = st.date_input("終了日", value=df_filtered['日付'].max(), key="p1_end")

        with col2:
            st.markdown("**期間2**")
            date2_start = st.date_input("開始日", value=df_filtered['日付'].min(), key="p2_start")
            date2_end = st.date_input("終了日", value=df_filtered['日付'].max(), key="p2_end")

        # 各期間のデータを抽出
        df_period1 = df_filtered[
            (pd.to_datetime(df_filtered['日付']) >= pd.to_datetime(date1_start)) &
            (pd.to_datetime(df_filtered['日付']) <= pd.to_datetime(date1_end))
        ]

        df_period2 = df_filtered[
            (pd.to_datetime(df_filtered['日付']) >= pd.to_datetime(date2_start)) &
            (pd.to_datetime(df_filtered['日付']) <= pd.to_datetime(date2_end))
        ]

        # KPI計算
        sales1, orders1, avg1, cust1 = calc_kpi(df_period1)
        sales2, orders2, avg2, cust2 = calc_kpi(df_period2)

        # 比較テーブル
        st.subheader("KPI比較")
        comparison_data = {
            '指標': ['総売上', '注文数', '平均注文金額', '顧客数'],
            '期間1': [f'¥{sales1:,.0f}', f'{orders1:,}件', f'¥{avg1:,.0f}', f'{cust1:,}人'],
            '期間2': [f'¥{sales2:,.0f}', f'{orders2:,}件', f'¥{avg2:,.0f}', f'{cust2:,}人'],
            '変化率': [
                f'{((sales2-sales1)/sales1*100) if sales1 > 0 else 0:+.1f}%' if sales1 > 0 else 'N/A',
                f'{((orders2-orders1)/orders1*100) if orders1 > 0 else 0:+.1f}%' if orders1 > 0 else 'N/A',
                f'{((avg2-avg1)/avg1*100) if avg1 > 0 else 0:+.1f}%' if avg1 > 0 else 'N/A',
                f'{((cust2-cust1)/cust1*100) if cust1 > 0 else 0:+.1f}%' if cust1 > 0 else 'N/A'
            ]
        }
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

        # 日別売上比較グラフ
        st.subheader("日別売上比較")
        daily1 = df_period1.groupby('日付')['金額'].sum().reset_index()
        daily1.columns = ['日付', '売上']
        daily1['期間'] = '期間1'

        daily2 = df_period2.groupby('日付')['金額'].sum().reset_index()
        daily2.columns = ['日付', '売上']
        daily2['期間'] = '期間2'

        daily_combined = pd.concat([daily1, daily2], ignore_index=True)

        fig_comparison = go.Figure()
        for period in ['期間1', '期間2']:
            data = daily_combined[daily_combined['期間'] == period]
            fig_comparison.add_trace(
                go.Scatter(x=data['日付'], y=data['売上'], mode='lines', name=period,
                           hovertemplate='<b>%{x}</b><br>売上: ¥%{y:,.0f}')
            )

        fig_comparison.update_layout(
            title='日別売上比較',
            xaxis_title='日付',
            yaxis_title='売上（円）',
            height=400,
            hovermode='x unified',
            template='plotly_white'
        )
        st.plotly_chart(fig_comparison, use_container_width=True)
    else:
        st.warning("⚠️ 期間比較に必要なデータが不足しています")
