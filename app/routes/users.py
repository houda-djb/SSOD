from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db
from app.models.user import User
import bcrypt

bp = Blueprint('users', __name__)


def require_admin():
    """
    Fetches the current user by ID (identity = str(user.id) set in auth.py).
    Returns (user, None) on success, or (None, error_response) on failure.
    """
    current_id = get_jwt_identity()          # returns str(user.id)
    user = User.query.get(int(current_id))
    if not user:
        return None, (jsonify({'error': 'User not found'}), 404)
    if user.role != 'admin':
        return None, (jsonify({'error': 'Admin access required. This page is restricted.'}), 403)
    return user, None


# ── GET /api/users  ──────────────────────────────────
@bp.route('/', methods=['GET'])
@bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    _, err = require_admin()
    if err:
        return err

    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users]), 200


# ── GET /api/users/<id> ──────────────────────────────
@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    _, err = require_admin()
    if err:
        return err

    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


# ── PUT /api/users/<id>/role ─────────────────────────
@bp.route('/<int:user_id>/role', methods=['PUT'])
@jwt_required()
def update_role(user_id):
    admin, err = require_admin()
    if err:
        return err

    user = User.query.get_or_404(user_id)

    if user.id == admin.id:
        return jsonify({'error': 'Cannot change your own role'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    new_role = data.get('role', '').strip().lower()

    if new_role not in ['admin', 'operator', 'viewer']:
        return jsonify({'error': 'Invalid role. Must be: admin, operator, or viewer'}), 400

    old_role = user.role
    user.role = new_role
    db.session.commit()

    return jsonify({
        'message': f'Role updated: {old_role} → {new_role}',
        'user': user.to_dict()
    }), 200


# ── PUT /api/users/<id>/toggle ───────────────────────
@bp.route('/<int:user_id>/toggle', methods=['PUT'])
@jwt_required()
def toggle_user(user_id):
    admin, err = require_admin()
    if err:
        return err

    user = User.query.get_or_404(user_id)

    if user.id == admin.id:
        return jsonify({'error': 'Cannot deactivate your own account'}), 400

    user.is_active = not user.is_active
    db.session.commit()

    state = 'activated' if user.is_active else 'deactivated'
    return jsonify({
        'message': f'User {user.username} has been {state}',
        'user': user.to_dict()
    }), 200


# ── POST /api/users/create ───────────────────────────
@bp.route('/create', methods=['POST'])
@jwt_required()
def create_user():
    _, err = require_admin()
    if err:
        return err

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    username = data.get('username', '').strip()
    email    = data.get('email', '').strip()
    password = data.get('password', '')
    role     = data.get('role', 'viewer').strip().lower()

    if not username or not email or not password:
        return jsonify({'error': 'username, email and password are required'}), 400

    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    if role not in ['admin', 'operator', 'viewer']:
        return jsonify({'error': 'Invalid role. Must be: admin, operator, or viewer'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    hashed = bcrypt.hashpw(
        password.encode('utf-8'), bcrypt.gensalt()
    ).decode('utf-8')

    new_user = User(
        username=username,
        email=email,
        password_hash=hashed,
        role=role,
        is_active=True
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'message': f'User {username} created successfully',
        'user': new_user.to_dict()
    }), 201