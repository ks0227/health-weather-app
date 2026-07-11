# 体調 × 天気 分析システム

![CI](https://github.com/ks0227/health-weather-app/actions/workflows/ci.yml/badge.svg)

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

| ページ             | 内容                                    |
| ------------------ | --------------------------------------- |
| トップページ       | Bootstrapカルーセル採用のナビゲーション |
| 体調入力フォーム   | 気分・睡眠・症状をWebフォームから記録   |
| 分析ダッシュボード | 相関ヒートマップ・トレンドグラフを表示  |
| 記録管理ページ     | 過去の体調ログを一覧・編集・削除        |

---

## ✨ 主な機能

- **体調ログ記録**：気分スコア（1〜5）・睡眠時間・症状・メモをWebフォームから入力（前日以前のみ登録可）
- **天気データ自動取得**：体調記録と同時に気象データを自動保存
  - Open-Meteo API（過去データ・無料・APIキー不要）
  - OpenWeatherMap API（当日の天気）
- **気象変化データの記録**：
  - 前日の気圧変化（前日 − 前々日）
  - 前日の気圧変化幅（1日の最大 − 最小）
  - 前日の気温変化（前日 − 前々日）
  - 前日の湿度変化（前日 − 前々日）
- **相関分析**：Pandas / scipy を使ってスピアマン順位相関係数・p値を計算
  - 気分スコアが順序尺度であることを考慮しスピアマン相関を採用
  - p値を2段階（p<0.05 / p<0.10）で表示し統計的信頼性を可視化
  - 当日データだけでなく前日の気象変化も分析対象に含める
- **ダッシュボード**：Plotly による相関ヒートマップと気分・気圧・気温・湿度の7日移動平均トレンドグラフ
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
| フロントエンド | HTML / CSS / JavaScript / Bootstrap 5.3 / Bootstrap Icons    |
| ホスティング   | Render                                                       |
| コード品質     | Ruff（Linter / Formatter）                                   |
| テスト         | pytest / pytest-flask                                        |
| CI/CD          | GitHub Actions                                               |

---

## 📁 ディレクトリ構成

```
.
├── main.py                  # アプリエントリポイント
├── database.py              # DB接続設定
├── models.py                # SQLAlchemyモデル定義
├── pyproject.toml           # Ruff・pytest設定
├── requirements.txt         # 依存ライブラリ一覧
├── .env.example             # 環境変数サンプル
├── .gitignore               # Git除外設定
├── routes/
│   ├── __init__.py
│   ├── health.py            # 体調ログ CRUD API
│   ├── weather.py           # 天気API連携（OpenWeatherMap / Open-Meteo）
│   ├── route_analysis.py    # 相関分析エンドポイント
│   └── dashboard.py         # ダッシュボード・入力フォーム・記録管理
├── services/
│   ├── __init__.py
│   └── analysis.py          # 分析ロジック（Pandas / scipy）
├── templates/
│   ├── index.html           # トップページ（Bootstrap carousel）
│   ├── dashboard.html       # ダッシュボード画面
│   ├── log_form.html        # 体調入力フォーム
│   └── records.html         # 記録管理ページ
└── tests/
    ├── __init__.py
    ├── conftest.py          # テスト共通設定
    ├── test_health_api.py   # APIエンドポイントのテスト
    └── test_analysis.py     # 分析ロジックのテスト
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

### 分析対象の気象指標

当日の気象データに加え、前日の変化量も分析対象に含めることで、体調への影響が翌日に現れる**ラグ効果**を検出します。

| 指標             | 内容                         |
| ---------------- | ---------------------------- |
| 気温             | その日の平均気温             |
| 湿度             | その日の最大湿度             |
| 気圧             | その日の平均気圧             |
| 前日の気圧変化   | 前日の気圧 − 前々日の気圧    |
| 前日の気圧変化幅 | 前日1日の最大気圧 − 最小気圧 |
| 前日の気温変化   | 前日の気温 − 前々日の気温    |
| 前日の湿度変化   | 前日の湿度 − 前々日の湿度    |

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
  "note": "低気圧っぽい", // 任意
  "date": "2024-01-01"   // 任意（省略時は昨日）※当日以降は登録不可
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

## 🧪 テスト

pytestによるテスト自動化を導入しています。

```bash
pytest tests/ -v
```

| テスト対象                                | 件数     |
| ----------------------------------------- | -------- |
| APIエンドポイント（CRUD・バリデーション） | 14件     |
| 分析ロジック（相関・トレンド）            | 16件     |
| **合計**                                  | **30件** |

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

## 🤖 CI/CD

GitHub Actionsによりpush時に自動でLint・テストが実行されます。

```
.github/workflows/ci.yml
├── Lint with Ruff
├── Format check with Ruff
└── Run tests (pytest)
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
