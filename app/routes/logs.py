from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db
from app.models.log import Log

bp = Blueprint("logs", __name__)


# ── GET /api/logs ────────────────────────────────────
@bp.route("/", methods=["GET"])
@bp.route("", methods=["GET"])
@jwt_required()
def get_logs():
    log_type = request.args.get('log_type')       # ?log_type=security
    source   = request.args.get('source')         # ?source=Auth
    limit    = request.args.get('limit', 100, type=int)
    offset   = request.args.get('offset', 0, type=int)
    limit    = min(limit, 500)

    query = Log.query

    if log_type:
        query = query.filter(Log.log_type == log_type)
    if source:
        query = query.filter(Log.source == source)

    logs = query.order_by(Log.timestamp.desc()).offset(offset).limit(limit).all()
    return jsonify([l.to_dict() for l in logs]), 200


# ── POST /api/logs/add ───────────────────────────────
@bp.route("/add", methods=["POST"])
@jwt_required()
def add_log():
    data = request.get_json()
    if not data or "action" not in data:
        return jsonify({"error": "action is required"}), 400

    current_id = get_jwt_identity()

    log = Log(
        user_id=int(current_id),
        source=data.get("source", "system"),
        log_type=data.get("log_type", "info"),
        action=data["action"],
        details=data.get("details"),
        ip_address=request.remote_addr,
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({"message": "Log added", "log": log.to_dict()}), 201