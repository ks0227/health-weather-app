import os
from datetime import date, timedelta

import requests
from dotenv import load_dotenv

from database import db
from models import WeatherData

load_dotenv()

LAT = float(os.getenv("LAT", 35.9))
LON = float(os.getenv("LON", 139.5))


def fetch_and_save_weather(target_date: date = None) -> WeatherData:
    """天気データを取得してDBに保存"""

    if target_date is None:
        target_date = date.today() - timedelta(days=1)

    existing = WeatherData.query.filter_by(date=target_date).first()
    if existing:
        return existing

    weather = fetch_historical_weather(target_date)
    weather = calc_pressure_change(weather, target_date)

    return weather


def fetch_historical_weather(target_date: date) -> WeatherData:
    """Open-Meteo APIで過去の天気データを取得"""

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": LAT,
        "longitude": LON,
        "start_date": str(target_date),
        "end_date": str(target_date),
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

    precipitation = daily.get("precipitation_sum", [None])[0] or 0
    if precipitation == 0:
        weather_desc = "晴れ"
    elif precipitation < 5:
        weather_desc = "小雨"
    else:
        weather_desc = "雨"

    weather = WeatherData(
        date=target_date,
        temperature=daily.get("temperature_2m_mean", [None])[0],
        humidity=daily.get("relative_humidity_2m_max", [None])[0],
        pressure=daily.get("pressure_msl_mean", [None])[0],
        weather_desc=weather_desc,
        pressure_change_prev=None,
        pressure_range_prev=None,
    )
    db.session.add(weather)
    db.session.commit()

    return weather


def fetch_pressure_range(target_date: date) -> float | None:
    """指定日の1日の気圧変化幅（最大-最小）をOpen-Meteoの時間別データから取得"""

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": LAT,
        "longitude": LON,
        "start_date": str(target_date),
        "end_date": str(target_date),
        "hourly": "pressure_msl",
        "timezone": "Asia/Tokyo",
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return None

    data = response.json()
    pressures = data.get("hourly", {}).get("pressure_msl", [])
    pressures = [p for p in pressures if p is not None]

    if not pressures:
        return None

    return round(max(pressures) - min(pressures), 1)


def calc_pressure_change(weather: WeatherData, target_date: date) -> WeatherData:
    """前日の気圧変化（前日-前々日）と前日の気圧変化幅を計算してDBを更新"""

    prev_date = target_date - timedelta(days=1)
    prev_prev_date = target_date - timedelta(days=2)

    prev_weather = WeatherData.query.filter_by(date=prev_date).first()
    if not prev_weather:
        try:
            prev_weather = fetch_historical_weather(prev_date)
        except Exception as e:
            print(f"前日データ取得エラー: {e}")
            return weather

    prev_prev_weather = WeatherData.query.filter_by(date=prev_prev_date).first()
    if not prev_prev_weather:
        try:
            prev_prev_weather = fetch_historical_weather(prev_prev_date)
        except Exception as e:
            print(f"前々日データ取得エラー: {e}")
            prev_prev_weather = None

    # 前日の気圧変化（前日 - 前々日）
    if prev_prev_weather and prev_weather.pressure is not None and prev_prev_weather.pressure is not None:
        weather.pressure_change_prev = round(prev_weather.pressure - prev_prev_weather.pressure, 1)

    # 前日の気圧変化幅（前日1日の最大-最小）
    if prev_weather.pressure_range_prev is None:
        try:
            range_value = fetch_pressure_range(prev_date)
            prev_weather.pressure_range_prev = range_value
        except Exception as e:
            print(f"気圧変化幅取得エラー: {e}")

    # 「前日の気圧変化幅」を記録日のweatherにも持たせる
    weather.pressure_range_prev = prev_weather.pressure_range_prev

    db.session.commit()

    return weather
