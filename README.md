# EC販売分析ダッシュボード

Streamlit を使った販売分析ダッシュボードです。

## 🚀 起動方法

### Windows
`run_dashboard.bat` をダブルクリック

### コマンドライン
```bash
streamlit run main_process.py
```

ブラウザが自動で開き、`http://localhost:8501` で表示されます。

---

## 📊 機能

- 📈 売上トレンド分析
- 🏆 ベストセラー商品ランキング
- 📊 期間比較分析
- 🔍 複数フィルタ機能（発送日、店舗名、配送便など）

---

## 🔄 データ更新方法

Google Drive のデータを更新した場合：

### 方法 1: フォルダを削除（推奨）
1. `クロスモールCSV` フォルダを削除
2. アプリを再起動 → 自動的に Google Drive から最新データをダウンロード

### 方法 2: コマンドで削除
```bash
rmdir /s クロスモールCSV
```
その後、アプリを再起動してください。

---

## 📁 ファイル構成

```
.
├── main_process.py          # Streamlit メインアプリ
├── load_csv.py              # Google Drive CSV ロード
├── utils.py                 # ユーティリティ関数
├── filters.py               # フィルタ機能
├── analysis_tabs.py         # 分析タブ
├── requirements.txt         # Python 依存関係
├── run_dashboard.bat        # Windows 起動スクリプト
├── .gitignore               # Git 除外ファイル
└── クロスモールCSV/         # データキャッシュ（Git管理外）
```

---

## ⚙️ セットアップ（初回のみ）

```bash
pip install -r requirements.txt
```

---

## 🔒 セキュリティ

- CSV データは Git 管理対象外（`.gitignore`）
- 認証ファイルも除外済み
- GitHub に機密情報は公開されません

---

## 📝 データソース

- Google Drive フォルダ ID: `1XQAzPbCo2IpwCX_exXtp4Yr8bL6fz0ek`
- ファイル形式: CSV（Shift-JIS/UTF-8対応）
- 対応エンコーディング: utf-8, shift_jis, cp932, utf-8-sig

