from flask import Blueprint, jsonify, session
from flask_login import login_required, current_user
from models import Transaction
from sqlalchemy import func
from extensions import db

visualization = Blueprint("visualization", __name__)

# =========================
# GET VISUALIZATION DATA
# =========================
@visualization.route("/api/visualization-data", methods=["GET"])
@login_required
def get_visualization_data():

    latest_batch = session.get("latest_batch_id")

    if not latest_batch:
        return jsonify({
            "category_data": [],
            "daily_data": [],
            "monthly_data": []
        }), 200


    # =========================
    # CATEGORY PIE CHART
    # =========================
    category_data = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.batch_id == latest_batch
    ).group_by(Transaction.category).all()


    category_result = [
        {"category": c, "amount": float(a)}
        for c, a in category_data
    ]


    # =========================
    # DAILY SPENDING LINE CHART
    # =========================
    daily_data = db.session.query(
        Transaction.date,
        func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.batch_id == latest_batch
    ).group_by(Transaction.date).order_by(Transaction.date).all()


    daily_result = [
        {"date": str(d), "amount": float(a)}
        for d, a in daily_data
    ]


    # =========================
    # MONTHLY BAR CHART
    # =========================
    monthly_data = db.session.query(
        func.strftime("%Y-%m", Transaction.date),
        func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.batch_id == latest_batch
    ).group_by(func.strftime("%Y-%m", Transaction.date)).all()


    monthly_result = [
        {"month": m, "amount": float(a)}
        for m, a in monthly_data
    ]


    return jsonify({
        "category_data": category_result,
        "daily_data": daily_result,
        "monthly_data": monthly_result
    })