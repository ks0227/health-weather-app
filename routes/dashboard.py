from datetime import date, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for

from database import db
from models import HealthLog
from services.analysis import run_correlation_analysis

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():
    result = run_correlation_analysis()
    return render_template("dashboard.html", result=result)


@dashboard_bp.route("/log", methods=["GET"])
def log_form():
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    return render_template("log_form.html", yesterday=yesterday)


# フォーム送信
@dashboard_bp.route("/log", methods=["POST"])
def log_submit():
    mood_score  = request.form.get("mood_score")
    sleep_hours = request.form.get("sleep_hours")
    symptom     = request.form.get("symptom")
    note        = request.form.get("note")
    log_date    = request.form.get("date")

    if not mood_score:
        flash("気分スコアを選択してください", "error")
        return redirect(url_for("dashboard.log_form"))

    parsed_date = date.fromisoformat(log_date)

    # 当日以降の日付は登録不可
    if parsed_date >= date.today():
        flash("当日以降の日付は登録できません。前日までの日付を入力してください。", "error")
        return redirect(url_for("dashboard.log_form"))

    log = HealthLog(
        date        = parsed_date,
        mood_score  = int(mood_score),
        sleep_hours = float(sleep_hours) if sleep_hours else None,
        symptom     = symptom or None,
        note        = note or None,
    )
    db.session.add(log)
    db.session.commit()

    try:
        from routes.weather import fetch_and_save_weather
        fetch_and_save_weather(log.date)
    except Exception as e:
        print(f"天気取得エラー: {e}")

    flash(f"{log_date} の体調を記録しました！", "success")
    return redirect(url_for("dashboard.log_form"))


@dashboard_bp.route("/records")
def records():
    logs = HealthLog.query.order_by(HealthLog.date.desc()).all()
    return render_template("records.html", logs=logs)


@dashboard_bp.route("/records/<int:log_id>/edit", methods=["POST"])
def edit_record(log_id):
    log = HealthLog.query.get_or_404(log_id)

    mood_score = request.form.get("mood_score")
    sleep_hours = request.form.get("sleep_hours")

    if not mood_score:
        flash("気分スコアを選択してください", "error")
        return redirect(url_for("dashboard.records"))

    log.date = date.fromisoformat(request.form.get("date"))
    log.mood_score = int(mood_score)
    log.sleep_hours = float(sleep_hours) if sleep_hours else None
    log.symptom = request.form.get("symptom") or None
    log.note = request.form.get("note") or None

    db.session.commit()
    flash("記録を更新しました", "success")
    return redirect(url_for("dashboard.records"))


@dashboard_bp.route("/records/<int:log_id>/delete", methods=["POST"])
def delete_record(log_id):
    log = HealthLog.query.get_or_404(log_id)
    db.session.delete(log)
    db.session.commit()
    flash("記録を削除しました", "success")
    return redirect(url_for("dashboard.records"))
