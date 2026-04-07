from flask import Blueprint, request, jsonify, current_app
from models import db, User
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from extensions import mail
from flask_login import login_user, logout_user, login_required
import re

auth = Blueprint("auth", __name__)

# ======= PASSWORD VALIDATION =======
def validate_password(password):
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'
    return re.match(pattern, password)

# ======= TOKEN FUNCTIONS =======
def generate_token(email):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(email, salt="reset-salt")

def verify_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = serializer.loads(token, salt="reset-salt", max_age=expiration)
        return email
    except:
        return None

# ======= REGISTER =======
@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name", "")

    if not validate_password(password):
        return jsonify({"message": "Password too weak"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    hashed_pw = generate_password_hash(password)
    new_user = User(email=email, password=hashed_pw, name=name)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Registration successful"}), 201

# ======= LOGIN =======
@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    login_user(user)
    return jsonify({"message": "Login successful"}), 200

# ======= LOGOUT =======
@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200

# ======= FORGOT PASSWORD (SEND EMAIL) =======
@auth.route("/reset-password-request", methods=["POST"])
def reset_request():
    data = request.get_json()
    email = data.get("email")

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "Email not found"}), 404

    token = generate_token(email)

    reset_link = f"http://localhost:3000/reset-password/{token}"

    msg = Message(
        subject="Password Reset",
        sender=("Finance App", current_app.config["MAIL_USERNAME"]),
        recipients=[email]
    )

    msg.body = f"""
Hello,

Click the link below to reset your password:

{reset_link}

This link will expire in 1 hour.

- Finance App
"""

    mail.send(msg)

    return jsonify({"message": "Reset link sent to your email"}), 200

# ======= RESET PASSWORD =======
@auth.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):

    email = verify_token(token)

    if not email:
        return jsonify({"message": "Invalid or expired token"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    new_password = data.get("password")

    if not validate_password(new_password):
        return jsonify({"message": "Password too weak"}), 400

    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200