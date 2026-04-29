from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db
from app.models.metric import Metric
import psutil

bp = Blueprint("metrics", __name__)


# ── GET /api/metrics ─────────────────────────────────
@bp.route("/", methods=["GET"])
@bp.route("", methods=["GET"])
@jwt_required()
def get_metrics():
    metrics = Metric.query.order_by(Metric.recorded_at.desc()).limit(100).all()
    return jsonify([m.to_dict() for m in metrics]), 200


# ── GET /api/metrics/live ────────────────────────────
@bp.route("/live", methods=["GET"])
@jwt_required()
def get_live_metrics():
    cpu  = psutil.cpu_percent(interval=1)
    ram  = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    live = {
        "cpu": {
            "usage_percent": cpu,
            "unit": "%"
        },
        "ram": {
            "total_gb":      round(ram.total / (1024 ** 3), 2),
            "used_gb":       round(ram.used  / (1024 ** 3), 2),
            "usage_percent": ram.percent,
            "unit": "GB"
        },
        "disk": {
            "total_gb":      round(disk.total / (1024 ** 3), 2),
            "used_gb":       round(disk.used  / (1024 ** 3), 2),
            "usage_percent": disk.percent,
            "unit": "GB"
        }
    }
    return jsonify(live), 200


# ── GET /api/metrics/history ─────────────────────────
@bp.route("/history", methods=["GET"])
@jwt_required()
def get_history():
    limit = request.args.get('limit', 50, type=int)
    limit = min(limit, 200)

    metrics = Metric.query.order_by(
        Metric.recorded_at.desc()
    ).limit(limit).all()

    # Reverse so oldest is first — correct order for chart rendering
    return jsonify([m.to_dict() for m in reversed(metrics)]), 200


# ── POST /api/metrics/add ────────────────────────────
@bp.route("/add", methods=["POST"])
@jwt_required()
def add_metric():
    data = request.get_json()
    if not data or not all(k in data for k in ["metric_type", "metric_name", "value"]):
        return jsonify({"error": "metric_type, metric_name and value are required"}), 400

    metric = Metric(
        source=data.get("source", "main_server"),
        metric_type=data["metric_type"],
        metric_name=data["metric_name"],
        value=data["value"],
        unit=data.get("unit"),
        threshold_breached=data.get("threshold_breached", False),
        threshold_value=data.get("threshold_value"),
    )
    db.session.add(metric)
    db.session.commit()
    return jsonify({"message": "Metric recorded", "metric": metric.to_dict()}), 201