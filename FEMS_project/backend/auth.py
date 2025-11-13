# backend/auth.py
from flask import Blueprint, request, jsonify, current_app
from .extensions import db
from .models import User, EmailVerification  # import any models you need
from .utils import hash_password, check_password, create_token, decode_token
from datetime import datetime, timedelta
from functools import wraps

bp = Blueprint("auth", __name__, url_prefix="/api")

def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization header required"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            data = decode_token(token)
            user = User.query.get(data.get("user_id"))
            if not user:
                return jsonify({"error": "User not found"}), 401
            return f(user, *args, **kwargs)
        except Exception as e:
            # jwt.ExpiredSignatureError or jwt.InvalidTokenError bubble as Exception
            return jsonify({"error": str(e)}), 401
    return wrapper

@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    required = ["email", "password", "full_name", "phone", "role"]
    for r in required:
        if r not in data or not data[r]:
            return jsonify({"error": f"{r} is required"}), 400

    email = data["email"].lower().strip()
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    if len(data["password"]) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    hashed = hash_password(data["password"])
    new_user = User(
        email=email,
        password_hash=hashed,
        role=data["role"].lower(),
        full_name=data["full_name"].strip(),
        phone=data["phone"].strip()
    )
    try:
        db.session.add(new_user)
        db.session.commit()
        # optionally: create verification code in EmailVerification here if required
        return jsonify({"message": "User registered", "user": new_user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500

@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    if "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password are required"}), 400

    email = data["email"].lower().strip()
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not check_password(data["password"], user.password_hash):
        return jsonify({"error": "Invalid credentials"}), 401

    # update last_login
    user.last_login = datetime.utcnow()
    db.session.commit()

    token = create_token(user.id, user.role)
    return jsonify({"message": "Login successful", "token": token, "user": user.to_dict()}), 200

@bp.route("/profile", methods=["GET"])
@token_required
def profile(current_user):
    return jsonify({"user": current_user.to_dict()}), 200
