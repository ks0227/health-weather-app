import pandas as pd
from scipy import stats
from models import HealthLog, WeatherData
from database import db


# =========================
# Data Layer
# =========================
def fetch_health_data():
    return db.session.query(HealthLog).all()


def fetch_weather_data():
    return db.session.query(WeatherData).all()


def to_dataframe(health_rows, weather_rows):
    df_health = pd.DataFrame([{
        "date": r.date,
        "mood_score": r.mood_score,
        "sleep_hours": r.sleep_hours,
    } for r in health_rows])

    df_weather = pd.DataFrame([{
        "date": r.date,
        "temperature": r.temperature,
        "humidity": r.humidity,
        "pressure": r.pressure,
    } for r in weather_rows])

    return df_health, df_weather


# =========================
# Preprocessing Layer
# =========================
def prepare_dataset(df_health, df_weather):
    df = pd.merge(df_health, df_weather, on="date", how="inner")

    # 日付不足チェック（ユニーク基準）
    if df["date"].nunique() < 7:
        return None, "体調と天気が一致する日が7日分以上ありません。"

    # 欠損処理（安全版）
    df = df.dropna()

    # 型保証
    df["date"] = pd.to_datetime(df["date"])

    return df.sort_values("date"), None


# =========================
# Analysis Layer
# =========================
def compute_correlations(df):
    health_cols = ["mood_score", "sleep_hours"]
    weather_cols = ["temperature", "humidity", "pressure"]

    results = []

    for hc in health_cols:
        for wc in weather_cols:

            r, p = stats.spearmanr(df[hc], df[wc])

            if pd.isna(r) or pd.isna(p):
                continue

            results.append({
                "health": hc,
                "weather": wc,
                "r": round(float(r), 3),
                "p": round(float(p), 4),
                "significant_05": bool(p < 0.05),
                "significant_10": bool(p < 0.1),
                "strength": classify_strength(r),
                "direction": "positive" if r > 0 else "negative",
                "summary": summarize(hc, wc, r, p)
            })

    return results


def compute_trend(df):
    df = df.copy()

    df["mood_7d"] = (
        df["mood_score"]
        .rolling(7, min_periods=7)
        .mean()
        .round(2)
    )

    df["pressure_7d"] = (
        df["pressure"]
        .rolling(7, min_periods=7)
        .mean()
        .round(2)
    )

    # NaN を None に変換（JSON対応）
    df = df.where(pd.notnull(df), other=None)

    return df[[
        "date",
        "mood_score",
        "mood_7d",
        "pressure",
        "pressure_7d"
    ]].assign(date=df["date"].astype(str)).to_dict("records")


# =========================
# Utility Layer
# =========================
def classify_strength(r):
    abs_r = abs(r)
    if abs_r >= 0.7:
        return "強く"
    elif abs_r >= 0.4:
        return "やや"
    else:
        return "弱く"


def summarize(health_col, weather_col, r, p):
    if p >= 0.1:
        return "明確な関係は見られません"

    strength = classify_strength(r)

    health_map = {
        "mood_score": "気分",
        "sleep_hours": "睡眠時間"
    }

    weather_map = {
        "temperature": "気温",
        "humidity": "湿度",
        "pressure": "気圧"
    }

    h = health_map[health_col]
    w = weather_map[weather_col]

    if r > 0:
        return f"{w}が上がると{h}が{strength}良くなる傾向"
    else:
        return f"{w}が上がると{h}が{strength}悪くなる傾向"


# =========================
# Main API Function
# =========================
def run_correlation_analysis():
    """体調×天気の相関分析API（production版）"""

    health_rows = fetch_health_data()
    weather_rows = fetch_weather_data()

    df_health, df_weather = to_dataframe(health_rows, weather_rows)

    df, error = prepare_dataset(df_health, df_weather)
    if error:
        return {"error": error}

    correlations = compute_correlations(df)
    trend = compute_trend(df)

    return {
        "data_count": len(df),
        "correlation_method": "spearman",
        "correlations": correlations,
        "trend": trend,
    }