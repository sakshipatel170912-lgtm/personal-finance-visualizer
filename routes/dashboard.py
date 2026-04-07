from flask import Blueprint, jsonify
from flask_login import login_required, current_user

dashboard = Blueprint("dashboard", __name__)

@dashboard.route("/api/dashboard", methods=["GET"])
@login_required
def get_dashboard():
    return jsonify({
        "user": {  
            "name": current_user.name if hasattr(current_user, 'name') else "",
            "email": current_user.email,
            "is_admin": current_user.is_admin if hasattr(current_user, 'is_admin') else False   # ✅ ADD THIS
        },
        "total_spent": 12000,
        "budget": 20000,
        "savings": 8000
    })