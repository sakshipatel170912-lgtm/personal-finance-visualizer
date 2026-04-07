from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required, current_user
from extensions import db
from models import User, Transaction
from datetime import datetime

# PDF imports
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from io import BytesIO

admin = Blueprint("admin", __name__)

# =========================================
# ADMIN CHECK
# =========================================
def admin_required():
    if not current_user.is_authenticated or not current_user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403


# =========================================
# LOG MODEL
# =========================================
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    action = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================
# SAVE LOG
# =========================================
def save_log(user_id, action):
    log = Log(user_id=user_id, action=action)
    db.session.add(log)
    db.session.commit()


# =========================================
# USERS
# =========================================
@admin.route("/users", methods=["GET"])
@login_required
def get_users():
    check = admin_required()
    if check:
        return check

    users = User.query.all()

    return jsonify([
        {
            "id": u.id,
            "name": u.name,
            "email": u.email
        } for u in users
    ])


# =========================================
# DELETE USER
# =========================================
@admin.route("/delete-user/<int:user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id):
    check = admin_required()
    if check:
        return check

    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    Transaction.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()

    save_log(current_user.id, f"Deleted user {user.email}")

    return jsonify({"message": "User deleted"})


# =========================================
# RESET USER
# =========================================
@admin.route("/reset-user/<int:user_id>", methods=["POST"])
@login_required
def reset_user(user_id):
    check = admin_required()
    if check:
        return check

    Transaction.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    save_log(current_user.id, f"Reset user {user_id}")

    return jsonify({"message": "User reset"})


# =========================================
# LOGS
# =========================================
@admin.route("/logs", methods=["GET"])
@login_required
def get_logs():
    check = admin_required()
    if check:
        return check

    logs = Log.query.order_by(Log.timestamp.desc()).limit(50)

    return jsonify([
        {
            "user_id": l.user_id,
            "action": l.action,
            "time": l.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for l in logs
    ])


# =========================================
# REPORT (JSON)
# =========================================
@admin.route("/report", methods=["GET"])
@login_required
def generate_report():
    check = admin_required()
    if check:
        return check

    total_users = User.query.count()
    total_transactions = Transaction.query.count()

    total_spent = db.session.query(
        db.func.sum(Transaction.amount)
    ).scalar() or 0

    month = datetime.utcnow().month
    year = datetime.utcnow().year

    monthly_spent = db.session.query(
        db.func.sum(Transaction.amount)
    ).filter(
        db.extract('month', Transaction.date) == month,
        db.extract('year', Transaction.date) == year
    ).scalar() or 0

    return jsonify({
        "total_users": total_users,
        "total_transactions": total_transactions,
        "total_spent": float(total_spent),
        "monthly_spent": float(monthly_spent)
    })


# =========================================
# PDF DOWNLOAD
# =========================================
@admin.route("/report/pdf", methods=["GET"])
@login_required
def download_pdf():
    check = admin_required()
    if check:
        return check

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    # DATA
    total_users = User.query.count()
    total_transactions = Transaction.query.count()

    total_spent = db.session.query(
        db.func.sum(Transaction.amount)
    ).scalar() or 0

    month = datetime.utcnow().month
    year = datetime.utcnow().year

    monthly_spent = db.session.query(
        db.func.sum(Transaction.amount)
    ).filter(
        db.extract('month', Transaction.date) == month,
        db.extract('year', Transaction.date) == year
    ).scalar() or 0

    # CONTENT
    elements = []

    elements.append(Paragraph("Admin Report", styles["Title"]))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph(f"Total Users: {total_users}", styles["Normal"]))
    elements.append(Paragraph(f"Total Transactions: {total_transactions}", styles["Normal"]))
    elements.append(Paragraph(f"Total Spent: ₹{total_spent}", styles["Normal"]))
    elements.append(Paragraph(f"This Month: ₹{monthly_spent}", styles["Normal"]))

    doc.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="admin_report.pdf",
        mimetype="application/pdf"
    )


# =========================================
# MAKE ADMIN
# =========================================
@admin.route("/make-admin/<int:user_id>", methods=["POST"])
def make_admin(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    user.is_admin = True
    db.session.commit()

    return jsonify({"message": "User is now admin"})