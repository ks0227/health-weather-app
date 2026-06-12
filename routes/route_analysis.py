from flask import Blueprint, jsonify

from services.analysis import run_correlation_analysis

analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.route("/analysis", methods=["GET"])
def get_analysis():
    result = run_correlation_analysis()
    return jsonify(result)
