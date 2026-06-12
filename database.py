import os

from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

db = SQLAlchemy()


def init_db(app):
    uri = os.getenv("DATABASE_URL", "sqlite:///health.db")

    # RenderのPostgreSQL URLを SQLAlchemy対応の形式に修正
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        from models import HealthLog, WeatherData

        db.create_all()
