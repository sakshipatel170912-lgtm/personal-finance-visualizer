from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for
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
    # Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char
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
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    # Handle both JSON (React/API) and Form data (Standard HTML)
    data = request.get_json() if request.is_json else request.form
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

    # After registration, send them to login
    return redirect(url_for('auth.login'))

# ======= LOGIN =======
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    data = request.get_json() if request.is_json else request.form
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    login_user(user)
    
    # After login, go to the dashboard
    # Note: Ensure your dashboard blueprint has a function named 'main_dashboard'
    return redirect(url_for('dashboard.dashboard'))

# ======= LOGOUT =======
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# ======= FORGOT PASSWORD =======
@auth.route("/reset-password-request", methods=["POST"])
def reset_request():
    data = request.get_json() if request.is_json else request.form
    email = data.get("email")

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "Email not found"}), 404

    token = generate_token(email)
    
    # Use request.url_root to automatically get your Vercel URL
    reset_link = f"{request.url_root}reset-password/{token}"

    msg = Message(
        subject="Password Reset",
        sender=("Finance App", current_app.config["MAIL_USERNAME"]),
        recipients=[email]
    )

    msg.body = f"Click here to reset your password: {reset_link}"
    mail.send(msg)

    return jsonify({"message": "Reset link sent to your email"}), 200

# ======= RESET PASSWORD =======
@auth.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):
    email = verify_token(token)

    if not email:
        return jsonify({"message": "Invalid or expired token"}), 400

    user = User.query.filter_by(email=email).first()
    data = request.get_json() if request.is_json else request.form
    new_password = data.get("password")

    if not validate_password(new_password):
        return jsonify({"message": "Password too weak"}), 400

    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200
