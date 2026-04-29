from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db
from app.models.alert import Alert
from datetime import datetime, timezone

bp = Blueprint("alerts", __name__)


# ── GET /api/alerts ──────────────────────────────────
@bp.route("/", methods=["GET"])
@bp.route("", methods=["GET"])
@jwt_required()
def get_alerts():
    category = request.args.get('category')      # ?category=incident
    severity = request.args.get('severity')      # ?severity=critical
    status   = request.args.get('status')        # ?status=open
    limit    = request.args.get('limit', 100, type=int)
    limit    = min(limit, 500)

    # ── Build filtered query (was ignored before — now correctly applied) ──
    query = Alert.query

    if category:
        query = query.filter(Alert.category == category)
    if severity:
        query = query.filter(Alert.severity == severity)
    if status:
        query = query.filter(Alert.status == status)

    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    return jsonify([a.to_dict() for a in alerts]), 200


# ── POST /api/alerts/add ─────────────────────────────
@bp.route("/add", methods=["POST"])
@jwt_required()
def add_alert():
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "title is required"}), 400

    current_id = get_jwt_identity()

    alert = Alert(
        user_id=int(current_id),
        severity=data.get("severity", "low"),
        category=data.get("category", "system"),
        title=data["title"],
        description=data.get("description"),
        source=data.get("source"),
    )
    db.session.add(alert)
    db.session.commit()
    return jsonify({"message": "Alert created", "alert": alert.to_dict()}), 201


# ── PUT /api/alerts/resolve/<id> ─────────────────────
@bp.route("/resolve/<int:alert_id>", methods=["PUT"])
@jwt_required()
def resolve_alert(alert_id):
    alert = Alert.query.get_or_404(alert_id)

    if alert.status == 'resolved':
        return jsonify({'error': 'Alert is already resolved'}), 400

    alert.status = 'resolved'
    alert.resolved_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({
        'message': f'Alert {alert_id} resolved successfully',
        'alert': alert.to_dict()
    }), 200