from load_data import get_dataframe
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')

# データ読み込み
print("=" * 60)
print("EC販売実績データ分析")
print("=" * 60)
df = get_dataframe()

# データ準備
print("\nデータ前処理中...")
# キャンセルフラグが True の行を除外
df = df[df['cancel_flag'] != True].copy()

# order_datetime を datetime に変換（タイムゾーン除去）
df['order_datetime'] = pd.to_datetime(df['order_datetime']).dt.tz_localize(None)
df['date'] = df['order_datetime'].dt.date
df['week'] = df['order_datetime'].dt.isocalendar().week
df['month'] = df['order_datetime'].dt.to_period('M')
df['year'] = df['order_datetime'].dt.year
df['year_month'] = df['order_datetime'].dt.strftime('%Y-%m')

print(f"  - キャンセル除外後の行数: {len(df):,}")
print(f"  - データ期間: {df['date'].min()} 〜 {df['date'].max()}")

# KPI 計算
total_sales = df['amount'].sum()
total_orders = df['order_number'].nunique()
avg_order_value = total_sales / total_orders if total_orders > 0 else 0
total_customers = df['customer_name'].nunique()

# ========================================
# 分析1: 売上トレンド分析
# ========================================
print("\n[1/3] 売上トレンド分析中...")

# 日別売上
daily_sales = df.groupby('date')['amount'].sum().reset_index()
daily_sales.columns = ['date', 'sales']

# 週別売上
weekly_sales = df.groupby(['year', 'week'])['amount'].sum().reset_index()
weekly_sales.columns = ['year', 'week', 'sales']

# 月別売上
monthly_sales = df.groupby('year_month')['amount'].sum().reset_index()
monthly_sales.columns = ['year_month', 'sales']
monthly_sales['year_month'] = pd.to_datetime(monthly_sales['year_month'])

# YoY比較用（年別月別）
yoy_data = df.groupby(['year', 'month'])['amount'].sum().reset_index()
yoy_data['month_str'] = yoy_data['month'].astype(str)

# グラフ1: 日別売上
fig_daily = go.Figure()
fig_daily.add_trace(
    go.Scatter(x=daily_sales['date'], y=daily_sales['sales'],
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
    go.Bar(x=monthly_sales['year_month'], y=monthly_sales['sales'],
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
for year in sorted(yoy_data['year'].unique()):
    year_data = yoy_data[yoy_data['year'] == year].sort_values('month')
    fig_yoy.add_trace(
        go.Scatter(x=year_data['month_str'], y=year_data['amount'],
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

# グラフ4: ベストセラー TOP 10
print("\n[2/3] ベストセラー分析中...")

bestseller = df.groupby('product_name').agg({
    'amount': 'sum',
    'quantity': 'sum'
}).reset_index()
bestseller.columns = ['product_name', 'sales', 'quantity']
bestseller = bestseller.sort_values('sales', ascending=False).head(10)

fig_bestseller = go.Figure()
fig_bestseller.add_trace(
    go.Bar(
        x=bestseller['sales'],
        y=bestseller['product_name'],
        orientation='h',
        marker=dict(color='#d62728'),
        text=bestseller['sales'].apply(lambda x: f'¥{x:,.0f}'),
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>売上: ¥%{x:,.0f}')
)
fig_bestseller.update_layout(
    title='ベストセラー TOP 10',
    xaxis_title='売上（円）',
    yaxis_title='',
    height=400,
    showlegend=False,
    hovermode='y',
    template='plotly_white'
)

# グラフ5: 販売予測（Prophet）
print("\n[3/3] 販売予測中...")

# 月別売上を Prophet フォーマットに
prophet_df = monthly_sales.copy()
prophet_df.columns = ['ds', 'y']
prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])

# Prophet モデルの学習
model = Prophet(yearly_seasonality=True, daily_seasonality=False)
model.fit(prophet_df)

# 将来6ヶ月の予測
future = model.make_future_dataframe(periods=6, freq='MS')
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
    title='販売予測（6ヶ月先まで）',
    xaxis_title='月',
    yaxis_title='売上（円）',
    height=400,
    hovermode='x unified',
    template='plotly_white'
)

# ========================================
# ダッシュボード HTML 生成
# ========================================
print("\nダッシュボード HTML を生成中...")

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>EC販売分析ダッシュボード</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f7fa;
            color: #333;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .kpi-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px 40px;
            background-color: white;
        }}
        .kpi-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .kpi-card h3 {{
            font-size: 0.9em;
            margin-bottom: 10px;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .kpi-card .value {{
            font-size: 2em;
            font-weight: bold;
        }}
        .charts-section {{
            padding: 30px 40px;
        }}
        .chart-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .chart-container {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        .footer {{
            text-align: center;
            padding: 30px;
            color: #999;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 EC販売分析ダッシュボード</h1>
        <p>販売トレンド・ベストセラー・予測の総合分析</p>
    </div>

    <div class="kpi-section">
        <div class="kpi-card">
            <h3>総売上</h3>
            <div class="value">¥{total_sales:,.0f}</div>
        </div>
        <div class="kpi-card">
            <h3>注文数</h3>
            <div class="value">{total_orders:,}</div>
        </div>
        <div class="kpi-card">
            <h3>平均注文金額</h3>
            <div class="value">¥{avg_order_value:,.0f}</div>
        </div>
        <div class="kpi-card">
            <h3>顧客数</h3>
            <div class="value">{total_customers:,}</div>
        </div>
    </div>

    <div class="charts-section">
        <div class="chart-row">
            <div class="chart-container">
                {fig_daily.to_html(include_plotlyjs='cdn', div_id='daily')}
            </div>
            <div class="chart-container">
                {fig_monthly.to_html(include_plotlyjs=False, div_id='monthly')}
            </div>
        </div>
        <div class="chart-row">
            <div class="chart-container">
                {fig_yoy.to_html(include_plotlyjs=False, div_id='yoy')}
            </div>
            <div class="chart-container">
                {fig_bestseller.to_html(include_plotlyjs=False, div_id='bestseller')}
            </div>
        </div>
        <div class="chart-row">
            <div class="chart-container" style="grid-column: 1/-1;">
                {fig_forecast.to_html(include_plotlyjs=False, div_id='forecast')}
            </div>
        </div>
    </div>

    <div class="footer">
        <p>📅 データ期間: {df['date'].min()} 〜 {df['date'].max()} | 🔄 最終更新: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""

with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

# ========================================
# 完了
# ========================================
print("\n" + "=" * 60)
print("✨ 分析完了！")
print("=" * 60)
print("\n📊 生成ファイル:")
print("  → dashboard.html (統合ダッシュボード)")
print("\n💡 機能:")
print("  ✓ KPI（総売上・注文数・平均注文金額・顧客数）")
print("  ✓ 日別売上推移")
print("  ✓ 月別売上")
print("  ✓ 年別比較（YoY）")
print("  ✓ ベストセラー TOP 10")
print("  ✓ 販売予測（6ヶ月先）")
print("\n🌐 ブラウザで dashboard.html を開いてご確認ください！")
print("=" * 60)
