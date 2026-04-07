from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from services.budget_service import (
    create_or_update_budget,
    get_budget_analysis,
    generate_budget_alerts,
    get_total_budget_summary,
    calculate_daily_spending_limit,
    CATEGORIES
)

budget = Blueprint("budget", __name__, url_prefix="/api")


# =========================
# GET CATEGORY LIST
# =========================
@budget.route("/categories", methods=["GET"])
@login_required
def get_categories():
    return jsonify(CATEGORIES), 200


# =========================
# SET OR UPDATE BUDGET
# =========================
@budget.route("/set-budget", methods=["POST"])
@login_required
def set_budget():

    data = request.get_json(silent=True) or {}

    category = data.get("category")
    monthly_budget = data.get("amount")
    month = data.get("month")
    year = data.get("year")

    if not category or monthly_budget is None or not month or not year:
        return jsonify({"error": "Missing fields"}), 400

    try:

        create_or_update_budget(
            current_user.id,
            category,
            monthly_budget,
            int(month),
            int(year)
        )

        return jsonify({
            "message": "Budget saved successfully"
        }), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================
# BUDGET ANALYSIS
# =========================
@budget.route("/budget-analysis", methods=["GET"])
@login_required
def budget_analysis():

    month = request.args.get("month")
    year = request.args.get("year")

    if not month or not year:
        return jsonify({"error": "Month and year required"}), 400

    try:

        analysis = get_budget_analysis(
            current_user.id,
            int(month),
            int(year)
        )

        alerts = generate_budget_alerts(
            current_user.id,
            analysis
        )

        return jsonify({
            "budget_data": analysis,
            "alerts": alerts
        }), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================
# TOTAL BUDGET SUMMARY
# =========================
@budget.route("/budget-summary", methods=["GET"])
@login_required
def budget_summary():

    month = request.args.get("month")
    year = request.args.get("year")

    if not month or not year:
        return jsonify({"error": "Month and year required"}), 400

    try:

        summary = get_total_budget_summary(
            current_user.id,
            int(month),
            int(year)
        )

        return jsonify(summary), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================
# DAILY SAFE SPENDING
# =========================
@budget.route("/daily-limit", methods=["GET"])
@login_required
def daily_limit():

    try:

        limit = calculate_daily_spending_limit(
            current_user.id
        )

        return jsonify({
            "daily_safe_spending": limit
        }), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500