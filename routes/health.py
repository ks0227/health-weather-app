from datetime import date

from flask import Blueprint, jsonify, request

from database import db
from models import HealthLog
from routes.weather import fetch_and_save_weather

health_bp = Blueprint("health", __name__)


# 体調ログを登録
@health_bp.route("/health", methods=["POST"])
def create_health_log():
    data = request.get_json()

    # 必須チェック
    if not data or "mood_score" not in data:
        return jsonify({"error": "mood_score は必須です"}), 400
    if not (1 <= data["mood_score"] <= 5):
        return jsonify({"error": "mood_score は1〜5で入力してください"}), 400

    log = HealthLog(
        date=data.get("date", date.today()),
        mood_score=data["mood_score"],
        sleep_hours=data.get("sleep_hours"),
        symptom=data.get("symptom"),
        note=data.get("note"),
    )
    db.session.add(log)
    db.session.commit()

    # 体調登録と同時に天気を自動取得 ← 追加
    try:
        fetch_and_save_weather(log.date)
    except Exception as e:
        print(f"天気取得エラー（無視して続行）: {e}")

    return jsonify(log.to_dict()), 201


# 体調ログを全件取得
@health_bp.route("/health", methods=["GET"])
def get_health_logs():
    logs = HealthLog.query.order_by(HealthLog.date.desc()).all()
    return jsonify([log.to_dict() for log in logs])


# 体調ログを1件取得
@health_bp.route("/health/<int:log_id>", methods=["GET"])
def get_health_log(log_id):
    log = HealthLog.query.get_or_404(log_id)
    return jsonify(log.to_dict())


# 体調ログを更新
@health_bp.route("/health/<int:log_id>", methods=["PUT"])
def update_health_log(log_id):
    log = HealthLog.query.get_or_404(log_id)
    data = request.get_json()

    if "mood_score" in data:
        if not (1 <= data["mood_score"] <= 5):
            return jsonify({"error": "mood_score は1〜5で入力してください"}), 400
        log.mood_score = data["mood_score"]

    log.sleep_hours = data.get("sleep_hours", log.sleep_hours)
    log.symptom = data.get("symptom", log.symptom)
    log.note = data.get("note", log.note)

    db.session.commit()
    return jsonify(log.to_dict())


# 体調ログを削除
@health_bp.route("/health/<int:log_id>", methods=["DELETE"])
def delete_health_log(log_id):
    log = HealthLog.query.get_or_404(log_id)
    db.session.delete(log)
    db.session.commit()
    return jsonify({"message": f"id={log_id} を削除しました"})
