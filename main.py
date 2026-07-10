import os

from flask import Flask, render_template

from database import init_db
from routes.analysis import analysis_bp
from routes.dashboard import dashboard_bp
from routes.health import health_bp

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "a3f8k2m9x7q1p4n6")
init_db(app)
app.register_blueprint(health_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(dashboard_bp)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # RenderはPORTを自動設定
    app.run(host="0.0.0.0", port=port)  # 0.0.0.0でリッスン
