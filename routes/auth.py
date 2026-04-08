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
    # If user visits the page (GET), show the register form
    if request.method == "GET":
        return render_template("register.html")

    # If user submits the form (POST), save the data
    data = request.form if request.form else request.get_json()
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

    return redirect(url_for('auth.login'))

# ======= LOGIN =======
@auth.route("/login", methods=["GET", "POST"])
def login():
    # If user visits the page (GET), show the login form
    if request.method == "GET":
        return render_template("login.html")

    # If user submits the form (POST), check credentials
    data = request.form if request.form else request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    login_user(user)
    # Redirect to your dashboard route
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
    data = request.form if request.form else request.get_json()
    email = data.get("email")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "Email not found"}), 404

    token = generate_token(email)
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
    data = request.form if request.form else request.get_json()
    new_password = data.get("password")

    if not validate_password(new_password):
        return jsonify({"message": "Password too weak"}), 400

    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200
