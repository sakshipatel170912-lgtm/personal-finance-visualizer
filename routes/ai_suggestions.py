from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from extensions import db
from models import Transaction
from sqlalchemy import func

ai_suggestions = Blueprint("ai_suggestions", __name__)

@ai_suggestions.route("/api/savings-suggestions", methods=["GET"])
@login_required
def savings_suggestions():

    month = request.args.get("month")

    if not month:
        return jsonify([])

    year = month.split("-")[0]
    month_num = month.split("-")[1]

    results = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label("spent")
    ).filter(
        Transaction.user_id == current_user.id,
        func.strftime("%Y", Transaction.date) == year,
        func.strftime("%m", Transaction.date) == month_num
    ).group_by(Transaction.category).all()

    suggestions = []

    for r in results:

        spent = r.spent or 0

        if spent > 5000:
            suggestion = f"You spent ₹{spent:.0f} on {r.category}. Reduce 25% to save ₹{spent*0.25:.0f}."

        elif spent > 2000:
            suggestion = f"You spent ₹{spent:.0f} on {r.category}. Cutting 15% can save ₹{spent*0.15:.0f}."

        elif spent > 1000:
            suggestion = f"You spent ₹{spent:.0f} on {r.category}. Try saving ₹{spent*0.10:.0f}."

        else:
            suggestion = f"Your spending in {r.category} is well controlled."

        suggestions.append({
            "category": r.category,
            "spent": round(spent, 2),
            "suggestion": suggestion
        })

    return jsonify(suggestions)