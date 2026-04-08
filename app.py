import os
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from extensions import db, mail, login_manager, migrate
from routes.auth import auth
from routes.dashboard import dashboard
from routes.statements import statements
from routes.visualization import visualization
from routes.budget import budget
from routes.ai_suggestions import ai_suggestions
from routes.chatbot import chatbot
from routes.profile import profile
from routes.admin import admin
from models import User

# This tells Flask to look in the 'templates' folder for HTML files
app = Flask(__name__, template_folder='templates')

# ================= CONFIG =================
app.config["SECRET_KEY"] = "finance_secret_key"

# VERCEL STORAGE FIX: Move SQLite to /tmp (the only writable folder)
if os.environ.get('VERCEL'):
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/database.db"
    app.instance_path = '/tmp'
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Session settings
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True

# ================= GMAIL CONFIG =================
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

# ================= CORS FIX =================
CORS(app, supports_credentials=True, origins=["*"])

# ================= INIT =================
db.init_app(app)
mail.init_app(app)
login_manager.init_app(app)
migrate.init_app(app, db)

login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"message": "Unauthorized"}), 401

# ================= REGISTER ROUTES =================
app.register_blueprint(auth)
app.register_blueprint(dashboard)
app.register_blueprint(statements)
app.register_blueprint(visualization)
app.register_blueprint(budget)
app.register_blueprint(ai_suggestions)
app.register_blueprint(chatbot)
app.register_blueprint(profile, url_prefix="/api")
app.register_blueprint(admin, url_prefix="/admin")

# ================= HOME ROUTE =================
@app.route("/")
def home():
    # This renders the Bootstrap HTML file inside your templates folder
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
