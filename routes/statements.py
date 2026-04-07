from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from extensions import db
from models import Transaction, CategoryRule
import pandas as pd
import pdfplumber
import re
from datetime import datetime
import uuid

statements = Blueprint("statements", __name__)

# ======================== Helpers ========================
def auto_categorize(description, user_id):
    if not description:
        return "Uncategorized"

    description = description.lower().strip()

    rules = CategoryRule.query.filter_by(user_id=user_id).all()
    for rule in rules:
        if rule.keyword.lower() in description:
            return rule.category

    default_rules = {
        "amazon": "Shopping", "flipkart": "Shopping", "myntra": "Shopping",
        "zomato": "Food & Dining", "swiggy": "Food & Dining", "dominos": "Food & Dining",
        "pizza": "Food & Dining", "petrol": "Fuel", "fuel": "Fuel", "hpcl": "Fuel",
        "salary": "Salary", "upi": "Transfer", "phonepe": "Transfer", "gpay": "Transfer",
        "google pay": "Transfer", "paytm": "Transfer", "loan": "EMI", "emi": "EMI",
        "electricity": "Electricity", "torrent power": "Electricity", "rent": "Rent",
        "atm": "ATM Withdrawal", "netflix": "Subscription", "prime": "Subscription",
        "gym": "Gym", "medical": "Medical", "apollo": "Medical", "pharmacy": "Pharmacy",
        "school": "Education", "college": "Education", "insurance": "Insurance",
        "mutual fund": "Investment", "sip": "Investment", "stock": "Investment"
    }

    for keyword, category in default_rules.items():
        if keyword in description:
            return category

    return "Uncategorized"


def clean_description(text):
    text = re.sub(r"^\d{2}[/-]\d{2}[/-]\d{4}", "", text).strip()
    text = re.sub(r"\b(dr|cr)\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\d[\d,]*\.?\d*$", "", text).strip()

    if "/" in text:
        parts = text.split("/")
        return parts[-1].strip()

    return text.strip()


def format_date_safe(date_value):
    try:
        if isinstance(date_value, datetime):
            return date_value

        date_str = str(date_value).replace("-", "/").strip()
        return datetime.strptime(date_str, "%d/%m/%Y")
    except Exception as e:
        print("DATE ERROR: " , e)
        return None


# ======================== UPLOAD STATEMENT ========================
@statements.route("/api/upload-statement", methods=["POST"])
@login_required
def upload_statement():

    files = request.files.getlist("files")
    pdf_password = request.form.get("password")

    if not files:
        return jsonify({"message": "No files uploaded"}), 400

    batch_id = str(uuid.uuid4())
    session["latest_batch_id"] = batch_id

    rows_added = 0

    try:

        for file in files:

            filename = file.filename.lower()

            # ================= EXCEL =================
            if filename.endswith((".xlsx", ".xls")):

                df = pd.read_excel(file)

                df.columns = df.columns.str.strip().str.lower()

                date_col = next((c for c in df.columns if "date" in c), None)
                desc_col = next((c for c in df.columns if "desc" in c or "narration" in c), None)
                amount_col = next((c for c in df.columns if "amount" in c), None)

                if not date_col or not desc_col or not amount_col:
                    continue

                for _, row in df.iterrows():

                    try:

                        date = format_date_safe(row[date_col])
                        description = clean_description(str(row[desc_col]))
                        amount = float(str(row[amount_col]).replace(",", ""))

                        debit = abs(amount) if amount < 0 else 0
                        credit = amount if amount > 0 else 0

                        if date and description:

                            tx = Transaction(
                                user_id=current_user.id,
                                date=date,
                                description=description,
                                amount=amount,
                                debit=debit,
                                credit=credit,
                                category=auto_categorize(description, current_user.id),
                                batch_id=batch_id,
                                source="upload",
                                is_locked=True
                            )

                            db.session.add(tx)
                            rows_added += 1

                    except:
                        continue

            # ================= PDF =================
            elif filename.endswith(".pdf"):

                pdf = pdfplumber.open(file, password=pdf_password) if pdf_password else pdfplumber.open(file)

                with pdf:

                    for page in pdf.pages:

                        text = page.extract_text()

                        if not text:
                            continue

                        for line in text.split("\n"):

                            line = line.strip()

                            date_match = re.match(r"^\d{2}[/-]\d{2}[/-]\d{4}", line)

                            if not date_match:
                                continue

                            date = format_date_safe(date_match.group())

                            numbers = re.findall(r"\d{1,3}(?:,\d{3})*(?:\.\d+)?", line)

                            if not numbers:
                                continue

                            try:
                                amount = float(numbers[-1].replace(",", ""))
                            except:
                                continue

                            description = clean_description(line)

                            is_debit = "dr" in line.lower()
                            is_credit = "cr" in line.lower()

                            debit = amount if is_debit else 0
                            credit = amount if is_credit else 0

                            if date and description:

                                tx = Transaction(
                                    user_id=current_user.id,
                                    date=date,
                                    description=description,
                                    amount=amount,
                                    debit=debit,
                                    credit=credit,
                                    category=auto_categorize(description, current_user.id),
                                    batch_id=batch_id,
                                    source="upload",
                                    is_locked=True
                                )

                                db.session.add(tx)
                                rows_added += 1

        db.session.commit()

        return jsonify({
            "message": f"{rows_added} transactions uploaded successfully",
            "batch_id": batch_id
        }), 200

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "message": "Upload failed",
            "error": str(e)
        }), 500


# ======================== VIEW TRANSACTIONS ========================
@statements.route("/api/transactions/latest", methods=["GET"])
@login_required
def get_latest_uploaded_transactions():

    latest_batch = session.get("latest_batch_id")

    if not latest_batch:
        return jsonify([]) , 200
    
    transactions = Transaction.query.filter_by(
        user_id=current_user.id,
        batch_id=latest_batch
    ).order_by(Transaction.date.desc()).all()

    return jsonify([
        {
            "id": t.id,
            "date": t.date.strftime("%Y-%m-%d") if t.date else None,
            "description": t.description,
            "debit": t.debit,
            "credit": t.credit,
            "amount": t.amount,
            "category": t.category,
            "source": t.source,
            "batch_id": t.batch_id
        } for t in transactions
    ]), 200


# ======================== MANUAL TRANSACTION ========================
@statements.route("/api/transactions/manual", methods=["POST"])
@login_required
def add_manual_transaction():

    data = request.get_json()

    description = data.get("description")
    amount = data.get("amount")
    batch_id = data.get("batch_id")

    if not description or amount is None:
        return jsonify({"message": "Description and amount required"}), 400

    try:
        amount = float(amount)
    except:
        return jsonify({"message": "Invalid amount"}), 400

    date = data.get("date")
    if date:
        date = datetime.strptime(date, "%Y-%m-%d")
    else:
        date = datetime.now()
    batch_id = data.get("batch_id")

    debit = abs(amount) if amount < 0 else 0
    credit = amount if amount > 0 else 0

    tx = Transaction(
        user_id=current_user.id,
        date=date,
        batch_id=batch_id,
        description=clean_description(description),
        amount=amount,
        debit=debit,
        credit=credit,
        category=auto_categorize(description, current_user.id),
        source="manual",
        is_locked=False
    )

    db.session.add(tx)
    db.session.commit()

    return jsonify({
        "id": tx.id,
        "date": tx.date.strftime("%Y-%m-%d"),
        "description": tx.description,
        "debit": tx.debit,
        "credit": tx.credit,
        "amount": tx.amount,
        "category": tx.category
    }), 201


# ======================== DELETE ========================
@statements.route("/api/transactions/<int:id>", methods=["DELETE"])
@login_required
def delete_transaction(id):

    tx = Transaction.query.filter_by(id=id, user_id=current_user.id).first()

    if not tx:
        return jsonify({"message": "Transaction not found"}), 404

    db.session.delete(tx)
    db.session.commit()

    return jsonify({"message": "Deleted successfully"}), 200


# ======================== UPDATE CATEGORY ========================
@statements.route("/api/transactions/<int:id>", methods=["PUT"])
@login_required
def update_transaction(id):

    tx = Transaction.query.filter_by(id=id, user_id=current_user.id).first()

    if not tx:
        return jsonify({"message": "Transaction not found"}), 404

    data = request.get_json()

    if "category" in data:
        tx.category = data["category"]

    db.session.commit()

    return jsonify({"message": "Updated successfully"}), 200


# ======================== BATCH TRANSACTIONS ========================
@statements.route("/api/transactions/batch/<batch_id>", methods=["GET"])
@login_required
def get_transactions_by_batch(batch_id):

    transactions = Transaction.query.filter_by(
        user_id=current_user.id,
        batch_id=batch_id
    ).all()

    return jsonify([
        {
            "id": t.id,
            "date": t.date.strftime("%Y-%m-%d") if t.date else None,
            "description": t.description,
            "debit": t.debit,
            "credit": t.credit,
            "amount": t.amount,
            "category": t.category,
            "source": t.source,
            "is_locked": t.is_locked
        } for t in transactions
    ]), 200