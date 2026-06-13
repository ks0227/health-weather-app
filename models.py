from datetime import datetime, timezone

from database import db


class HealthLog(db.Model):
    __tablename__ = "health_logs"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.today)
    mood_score = db.Column(db.Integer, nullable=False)  # 1〜5の気分スコア
    sleep_hours = db.Column(db.Float)  # 睡眠時間
    symptom = db.Column(db.String(200))  # 頭痛・倦怠感など
    note = db.Column(db.Text)  # 自由メモ
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "date": str(self.date),
            "mood_score": self.mood_score,
            "sleep_hours": self.sleep_hours,
            "symptom": self.symptom,
            "note": self.note,
        }


class WeatherData(db.Model):
    __tablename__ = "weather_data"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    temperature = db.Column(db.Float)  # 気温（℃）
    humidity = db.Column(db.Integer)  # 湿度（%）
    pressure = db.Column(db.Float)  # 気圧（hPa）
    weather_desc = db.Column(db.String(100))  # 例: "曇り"

    def to_dict(self):
        return {
            "id": self.id,
            "date": str(self.date),
            "temperature": self.temperature,
            "humidity": self.humidity,
            "pressure": self.pressure,
            "weather_desc": self.weather_desc,
        }
