import requests
import os
from dotenv import load_dotenv
from datetime import date
from database import db
from models import WeatherData

load_dotenv()

# 川越市の緯度経度
LAT = float(os.getenv("LAT", 35.9))
LON = float(os.getenv("LON", 139.5))


def fetch_and_save_weather(target_date: date = None) -> WeatherData:
    """天気データを取得してDBに保存"""

    if target_date is None:
        target_date = date.today()

    # すでに同じ日のデータがあればそれを返す
    existing = WeatherData.query.filter_by(date=target_date).first()
    if existing:
        return existing

    # 今日または未来は現在の天気APIを使う
    if target_date >= date.today():
        return fetch_current_weather(target_date)
    else:
        return fetch_historical_weather(target_date)


def fetch_current_weather(target_date: date) -> WeatherData:
    """OpenWeatherMap APIで現在の天気を取得"""

    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    CITY    = os.getenv("CITY", "Kawagoe")

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q":     CITY,
        "appid": API_KEY,
        "units": "metric",
        "lang":  "ja",
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"天気API エラー: {response.status_code} {response.text}")

    data = response.json()

    weather = WeatherData(
        date         = target_date,
        temperature  = data["main"]["temp"],
        humidity     = data["main"]["humidity"],
        pressure     = data["main"]["pressure"],
        weather_desc = data["weather"][0]["description"],
    )
    db.session.add(weather)
    db.session.commit()

    return weather


def fetch_historical_weather(target_date: date) -> WeatherData:
    """Open-Meteo APIで過去の天気データを取得（無料・APIキー不要）"""

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude":   LAT,
        "longitude":  LON,
        "start_date": str(target_date),
        "end_date":   str(target_date),
        "daily": [
            "temperature_2m_mean",
            "relative_humidity_2m_max",
            "pressure_msl_mean",
            "precipitation_sum",
        ],
        "timezone": "Asia/Tokyo",
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"Open-Meteo エラー: {response.status_code} {response.text}")

    data = response.json()
    daily = data.get("daily", {})

    # 降水量から天気の説明を生成
    precipitation = daily.get("precipitation_sum", [None])[0] or 0
    if precipitation == 0:
        weather_desc = "晴れ"
    elif precipitation < 5:
        weather_desc = "小雨"
    else:
        weather_desc = "雨"

    weather = WeatherData(
        date         = target_date,
        temperature  = daily.get("temperature_2m_mean",    [None])[0],
        humidity     = daily.get("relative_humidity_2m_max",[None])[0],
        pressure     = daily.get("pressure_msl_mean",      [None])[0],
        weather_desc = weather_desc,
    )
    db.session.add(weather)
    db.session.commit()

    return weather