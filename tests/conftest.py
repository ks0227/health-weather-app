from datetime import date

import pytest

from database import db as _db
from main import app as flask_app
from models import HealthLog, WeatherData


@pytest.fixture(scope="session")
def app():
    flask_app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
        }
    )
    yield flask_app


@pytest.fixture(scope="session")
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app, db):
    with app.app_context():
        _db.session.query(HealthLog).delete()
        _db.session.query(WeatherData).delete()
        _db.session.commit()
        yield app.test_client()


@pytest.fixture(scope="function")
def sample_health_log(app, db):
    with app.app_context():
        log = HealthLog(
            date=date(2024, 1, 1),
            mood_score=4,
            sleep_hours=7.5,
            symptom="頭痛",
            note="テストデータ",
        )
        _db.session.add(log)
        _db.session.commit()
        # IDだけ取り出してセッションから切り離す
        log_id = log.id
    return log_id  # ← オブジェクトではなくIDを返す


@pytest.fixture(scope="function")
def sample_weather_data(app, db):
    with app.app_context():
        weather = WeatherData(
            date=date(2024, 1, 1),
            temperature=15.0,
            humidity=60,
            pressure=1013.0,
            weather_desc="晴れ",
        )
        _db.session.add(weather)
        _db.session.commit()
        weather_id = weather.id
    return weather_id
