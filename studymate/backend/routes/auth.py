from flask import Blueprint, request, jsonify
from database import get_db
import bcrypt
import jwt
import os
from datetime import datetime, timedelta

auth_bp = Blueprint("auth", __name__)


def make_token(user_id, email):
    payload = {
        "user_id": str(user_id),
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, os.getenv("SECRET_KEY", "secret"), algorithm="HS256")


def verify_token(token):
    try:
        return jwt.decode(
            token,
            os.getenv("SECRET_KEY", "secret"),
            algorithms=["HS256"]
        )
    except Exception:
        return None


def get_current_user():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    return verify_token(token)


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not name or not email or not password:
            return jsonify({"error": "All fields are required"}), 400

        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        db = get_db()

        # Check if email exists
        try:
            existing = db.table("users").select("id").eq("email", email).execute()
            if existing.data:
                return jsonify({"error": "Email already registered"}), 409
        except Exception as e:
            return jsonify({"error": f"Database error checking email: {str(e)}"}), 500

        # Hash password
        hashed = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # Insert user
        try:
            result = db.table("users").insert({
                "name": name,
                "email": email,
                "password_hash": hashed
            }).execute()
        except Exception as e:
            return jsonify({"error": f"Database error creating user: {str(e)}"}), 500

        if not result.data:
            return jsonify({"error": "Failed to create account"}), 500

        user = result.data[0]
        token = make_token(user["id"], user["email"])

        return jsonify({
            "message": "Account created successfully",
            "token": token,
            "user": {
                "id": str(user["id"]),
                "name": user["name"],
                "email": user["email"]
            }
        }), 201

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        db = get_db()
        result = db.table("users").select("*").eq("email", email).execute()

        if not result.data:
            return jsonify({"error": "Invalid email or password"}), 401

        user = result.data[0]

        if not bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        ):
            return jsonify({"error": "Invalid email or password"}), 401

        token = make_token(user["id"], user["email"])

        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": str(user["id"]),
                "name": user["name"],
                "email": user["email"]
            }
        })

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@auth_bp.route("/me", methods=["GET"])
def me():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db()
    result = db.table("users").select(
        "id, name, email, created_at"
    ).eq("id", user["user_id"]).execute()

    if not result.data:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": result.data[0]})