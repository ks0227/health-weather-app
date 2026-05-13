import requests
import os
from dotenv import load_dotenv
from datetime import date
from database import db
from models import WeatherData

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY    = os.getenv("CITY", "Tokyo")

def fetch_and_save_weather(target_date: date = None) -> WeatherData:
    """天気APIを叩いてDBに保存。体調登録時に自動で呼ばれる"""

    if target_date is None:
        target_date = date.today()

    # すでに同じ日のデータがあればそれを返す（二重取得を防ぐ）
    existing = WeatherData.query.filter_by(date=target_date).first()
    if existing:
        return existing

    # OpenWeatherMap API を呼び出す
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q":     CITY,
        "appid": API_KEY,
        "units": "metric",  # 摂氏
        "lang":  "ja",      # 天気説明を日本語で取得
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