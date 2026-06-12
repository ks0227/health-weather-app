# 🌤️ 個人生活データ分析システム（体調 × 天気）

体調と天気の相関を自動で分析・可視化するWebアプリケーションです。  
毎日の体調を記録するだけで、気圧・気温・湿度との関係をグラフで確認できます。

🔗 **デモ**: https://health-weather-app.onrender.com

---

## 📌 制作背景

「天気が悪い日は体調も悪い気がする」という経験をデータで検証したいと考え、本システムを開発しました。  
体調の記録・天気の自動取得・相関分析・可視化までを一貫して実装し、  
Webアプリとして実際に使える形に仕上げました。

---

## 🖥️ 画面構成

| ページ             | 内容                                   |
| ------------------ | -------------------------------------- |
| トップページ       | ナビゲーション                         |
| 体調入力フォーム   | 気分・睡眠・症状をWebフォームから記録  |
| 分析ダッシュボード | 相関ヒートマップ・トレンドグラフを表示 |
| 記録管理ページ     | 過去の体調ログを一覧・編集・削除       |

---

## ✨ 主な機能

- **体調ログ記録**：気分スコア（1〜5）・睡眠時間・症状・メモをWebフォームから入力
- **天気データ自動取得**：体調記録と同時に気象データを自動保存
  - 当日：OpenWeatherMap API（現在の天気）
  - 過去日付：Open-Meteo API（履歴データ・無料・APIキー不要）
- **相関分析**：Pandas / scipy を使ってスピアマン順位相関係数・p値を計算
  - 気分スコアが順序尺度であることを考慮しスピアマン相関を採用
  - p値を2段階（p<0.05 / p<0.10）で表示し統計的信頼性を可視化
- **ダッシュボード**：Plotly による相関ヒートマップと気分・気圧・気温・湿度の7日移動平均トレンドグラフを表示
- **REST API**：体調ログの登録・取得・更新・削除（CRUD）に対応
- **スマホ対応**：レスポンシブデザインでスマホからも記録・確認が可能

---

## 🛠️ 使用技術

| カテゴリ       | 技術                                                         |
| -------------- | ------------------------------------------------------------ |
| バックエンド   | Python 3.x / Flask                                           |
| データベース   | PostgreSQL（Supabase）/ SQLite（ローカル）/ Flask-SQLAlchemy |
| データ分析     | Pandas / scipy                                               |
| 可視化         | Plotly                                                       |
| 外部API        | OpenWeatherMap API / Open-Meteo API                          |
| フロントエンド | HTML / CSS / JavaScript                                      |
| ホスティング   | Render                                                       |
| コード品質     | Ruff（Linter / Formatter）                                   |

---

## 📁 ディレクトリ構成

```
.
├── main.py                  # アプリエントリポイント
├── database.py              # DB接続設定
├── models.py                # SQLAlchemyモデル定義
├── pyproject.toml           # Ruff設定
├── requirements.txt         # 依存ライブラリ一覧
├── .env.example             # 環境変数サンプル
├── routes/
│   ├── health.py            # 体調ログ CRUD API
│   ├── weather.py           # 天気API連携（OpenWeatherMap / Open-Meteo）
│   ├── route_analysis.py    # 相関分析エンドポイント
│   └── dashboard.py        # ダッシュボード・入力フォーム・記録管理
├── services/
│   └── analysis.py          # 分析ロジック（Pandas / scipy）
└── templates/
    ├── index.html           # トップページ
    ├── dashboard.html       # ダッシュボード画面
    ├── log_form.html        # 体調入力フォーム
    └── records.html         # 記録管理ページ
```

---

## 🚀 セットアップ手順

### 1. リポジトリをクローン

```bash
git clone https://github.com/ks0227/health-weather-app.git
cd health-weather-app
```

### 2. 仮想環境を作成・有効化

```bash
python -m venv venv

# Mac / Linux
source venv/bin/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

### 3. 依存ライブラリをインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数を設定

`.env.example` をコピーして `.env` を作成し、APIキーを設定します。

```bash
cp .env.example .env
```

```env
OPENWEATHER_API_KEY=your_api_key_here
CITY=Kawagoe
LAT=35.9
LON=139.5
```

> OpenWeatherMap の無料APIキーは [こちら](https://openweathermap.org/api) から取得できます。  
> Open-Meteo API はAPIキー不要です。

### 5. アプリを起動

```bash
python main.py
```

ブラウザで以下にアクセスします。

| URL                             | 内容                 |
| ------------------------------- | -------------------- |
| http://localhost:5000/          | トップページ         |
| http://localhost:5000/log       | 体調入力フォーム     |
| http://localhost:5000/dashboard | 分析ダッシュボード   |
| http://localhost:5000/records   | 記録管理ページ       |
| http://localhost:5000/health    | 体調ログ一覧（JSON） |
| http://localhost:5000/analysis  | 相関分析結果（JSON） |

---

## 📊 分析について

### 相関手法の選択理由

気分スコアは1〜5の**順序尺度**であるため、連続量を前提とするピアソン相関ではなく、**スピアマン順位相関**を採用しています。これにより、データの分布に依存しない頑健な相関分析が可能です。

### 相関係数（r）の目安

| r の値       | 意味             |
| ------------ | ---------------- |
| 0.7 以上     | 強い正の相関     |
| 0.4 〜 0.7   | 中程度の正の相関 |
| -0.4 〜 0.4  | ほぼ関係なし     |
| -0.7 〜 -0.4 | 中程度の負の相関 |
| -0.7 以下    | 強い負の相関     |

### 統計的有意性の表示

| バッジ         | 条件     | 意味                             |
| -------------- | -------- | -------------------------------- |
| 統計的に有意 ✓ | p < 0.05 | 信頼性が高い                     |
| 参考値         | p < 0.10 | 傾向として参考になる             |
| データ不足     | p ≥ 0.10 | データが増えると変わる可能性あり |

分析には **最低7日分** のデータが必要です。30日以上蓄積すると精度が上がります。

---

## 🔌 API仕様

### 体調ログ登録

```
POST /health
Content-Type: application/json

{
  "mood_score": 4,       // 必須：1〜5
  "sleep_hours": 7.5,    // 任意
  "symptom": "頭痛",     // 任意
  "note": "低気圧っぽい"  // 任意
}
```

### 体調ログ一覧取得

```
GET /health
```

### 相関分析結果取得

```
GET /analysis
```

---

## 🧹 コード品質

[Ruff](https://docs.astral.sh/ruff/) を導入しています。

```bash
# チェック
ruff check .

# 自動修正
ruff check --fix .

# フォーマット
ruff format .
```

---

## 📝 今後の予定

- [ ] ユーザー認証機能（Flask-Login）
- [ ] 週次レポートのメール自動送信
- [ ] 気圧急変時の体調悪化アラート
- [ ] Dockerコンテナ化
- [ ] 機械学習による翌日の体調予測

---

## 👤 作者

- GitHub: [@ks0227](https://github.com/ks0227)
