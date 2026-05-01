from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models import db
from app.models.user import User
from datetime import datetime, timezone
import bcrypt
import os

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data or not all(k in data for k in ["username", "email", "password"]):
        return jsonify({"error": "username, email and password are required"}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already exists"}), 409

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 409

    password_hash = bcrypt.hashpw(
        data["password"].encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    # FIX: First user ever registered automatically becomes admin
    is_first_user = User.query.count() == 0
    role = "admin" if is_first_user else data.get("role", "viewer")

    user = User(
        username=data["username"],
        email=data["email"],
        password_hash=password_hash,
        role=role,
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": f"User created successfully{'  — you are the first user, granted admin role!' if is_first_user else ''}",
        "user": user.to_dict()
    }), 201


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not all(k in data for k in ["username", "password"]):
        return jsonify({"error": "username and password are required"}), 400

    user = User.query.filter_by(username=data["username"]).first()

    if not user or not bcrypt.checkpw(
        data["password"].encode("utf-8"), user.password_hash.encode("utf-8")
    ):
        return jsonify({"error": "Invalid username or password"}), 401

    if not user.is_active:
        return jsonify({"error": "Account is disabled. Contact your administrator."}), 403

    user.last_login = datetime.now(timezone.utc)
    db.session.commit()

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": user.to_dict()
    }), 200