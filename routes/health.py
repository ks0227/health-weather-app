from datetime import date, datetime  # datetime を追加

from flask import Blueprint, jsonify, request

from database import db
from models import HealthLog
from routes.weather import fetch_and_save_weather

health_bp = Blueprint("health", __name__)


# 体調ログを登録
@health_bp.route("/health", methods=["POST"])
def create_health_log():
    data = request.get_json()

    if not data or "mood_score" not in data:
        return jsonify({"error": "mood_score は必須です"}), 400
    if not (1 <= data["mood_score"] <= 5):
        return jsonify({"error": "mood_score は1〜5で入力してください"}), 400

    # 日付の変換処理を追加
    raw_date = data.get("date")
    if raw_date:
        if isinstance(raw_date, str):
            log_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        else:
            log_date = raw_date
    else:
        log_date = date.today()

    log = HealthLog(
        date=log_date,  # ← 変換済みのdateオブジェクトを使用
        mood_score=data["mood_score"],
        sleep_hours=data.get("sleep_hours"),
        symptom=data.get("symptom"),
        note=data.get("note"),
    )
    db.session.add(log)
    db.session.commit()

    try:
        from routes.weather import fetch_and_save_weather

        fetch_and_save_weather(log.date)
    except Exception as e:
        print(f"天気取得エラー: {e}")

    return jsonify(log.to_dict()), 201


# 体調ログを全件取得
@health_bp.route("/health", methods=["GET"])
def get_health_logs():
    logs = HealthLog.query.order_by(HealthLog.date.desc()).all()
    return jsonify([log.to_dict() for log in logs])


# 体調ログを1件取得
@health_bp.route("/health/<int:log_id>", methods=["GET"])
def get_health_log(log_id):
    log = db.get_or_404(HealthLog, log_id)
    return jsonify(log.to_dict())


# 体調ログを更新
@health_bp.route("/health/<int:log_id>", methods=["PUT"])
def update_health_log(log_id):
    log = db.get_or_404(HealthLog, log_id)
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
    log = db.get_or_404(HealthLog, log_id)
    db.session.delete(log)
    db.session.commit()
    return jsonify({"message": f"id={log_id} を削除しました"})
