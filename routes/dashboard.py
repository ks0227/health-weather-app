from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.analysis import run_correlation_analysis
from models import HealthLog
from database import db
from datetime import date

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    result = run_correlation_analysis()
    return render_template("dashboard.html", result=result)

# フォーム表示
@dashboard_bp.route("/log", methods=["GET"])
def log_form():
    today = date.today().isoformat()
    return render_template("log_form.html", today=today)

# フォーム送信
@dashboard_bp.route("/log", methods=["POST"])
def log_submit():
    mood_score = request.form.get("mood_score")
    sleep_hours = request.form.get("sleep_hours")
    symptom = request.form.get("symptom")
    note = request.form.get("note")
    log_date = request.form.get("date")

    # バリデーション
    if not mood_score:
        flash("気分スコアを選択してください", "error")
        return redirect(url_for("dashboard.log_form"))

    log = HealthLog(
        date        = date.fromisoformat(log_date),
        mood_score  = int(mood_score),
        sleep_hours = float(sleep_hours) if sleep_hours else None,
        symptom     = symptom or None,
        note        = note or None,
    )
    db.session.add(log)
    db.session.commit()

    # 天気を自動取得
    try:
        from routes.weather import fetch_and_save_weather
        fetch_and_save_weather(log.date)
    except Exception as e:
        print(f"天気取得エラー: {e}")

    flash(f"{log_date} の体調を記録しました！", "success")
    return redirect(url_for("dashboard.log_form"))