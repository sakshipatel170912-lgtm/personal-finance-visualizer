from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import FinancialGoal
from werkzeug.security import generate_password_hash

profile = Blueprint("profile", __name__)


# ===============================
# GET PROFILE + GOALS (COMBINED)
# ===============================
@profile.route("/profile", methods=["GET"])
@login_required
def get_profile():
    user = current_user
    goal = user.financial_goal  # 🔥 using relationship

    return jsonify({
        "name": user.name,
        "email": user.email,
        "currency": user.currency,
        "theme": user.theme,
        "notifications": user.notifications,
        "saving_goal": goal.monthly_saving_goal if goal else 0,
        "budget": goal.monthly_budget if goal else 0
    })


# ===============================
# 🔥 UPDATE EVERYTHING (BEST API)
# ===============================
@profile.route("/profile/update-all", methods=["POST"])
@login_required
def update_all():
    try:
        data = request.json
        user = current_user

        # ================= PROFILE =================
        user.name = data.get("name", user.name)
        user.email = data.get("email", user.email)

        # ================= PASSWORD =================
        if data.get("password"):
            user.password = generate_password_hash(data["password"])

        # ================= PREFERENCES =================
        user.currency = data.get("currency", user.currency)
        user.theme = data.get("theme", user.theme)
        user.notifications = data.get("notifications", user.notifications)

        # ================= GOALS =================
        goal = user.financial_goal

        if goal:
            goal.monthly_saving_goal = data.get("saving_goal", goal.monthly_saving_goal)
            goal.monthly_budget = data.get("budget", goal.monthly_budget)
        else:
            goal = FinancialGoal(
                user_id=user.id,
                monthly_saving_goal=data.get("saving_goal", 0),
                monthly_budget=data.get("budget", 0)
            )
            db.session.add(goal)

        db.session.commit()

        return jsonify({
            "message": "All data updated successfully"
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({
            "error": "Failed to update profile"
        }), 500


# ===============================
# OPTIONAL: CHANGE PASSWORD ONLY
# ===============================
@profile.route("/profile/change-password", methods=["POST"])
@login_required
def change_password():
    try:
        data = request.json
        user = current_user

        if not data.get("password"):
            return jsonify({"error": "Password required"}), 400

        user.password = generate_password_hash(data["password"])
        db.session.commit()

        return jsonify({"message": "Password updated"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500