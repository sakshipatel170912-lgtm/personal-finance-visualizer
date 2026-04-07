from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import Transaction
from extensions import db
from sqlalchemy import func
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
import os

# Load .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("❌ GROQ_API_KEY not found.")

client = Groq(api_key=api_key)

chatbot = Blueprint("chatbot", __name__, url_prefix="/api")


@chatbot.route("/chatbot", methods=["POST"])
@login_required
def chatbot_response():

    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"reply": "Ask something about the finance app."})

    # ✅ Restrict unrelated questions
    allowed_keywords = [
        "budget", "expense", "upload", "chart",
        "dashboard", "finance", "money",
        "saving", "transaction"
    ]

    if not any(word in user_message.lower() for word in allowed_keywords):
        return jsonify({
            "reply": "❌ Ask only about Personal Finance Website features."
        })

    # ✅ Get top spending category
    top_category = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.user_id == current_user.id
    ).group_by(Transaction.category)\
     .order_by(func.sum(Transaction.amount).desc())\
     .first()

    spending_context = ""
    if top_category:
        spending_context = f"Top category: {top_category.category} ₹{top_category.total:.0f}"

    # ✅ STRICT PROMPT
    prompt = f"""
You are a Personal Finance Web App Assistant.

RULES:
- Answer ONLY about this website
- DO NOT write paragraphs
- Each line separate
- Max 6 lines
- Short clear answers

Features:
- Upload statements
- Expense tracking
- Charts dashboard
- Budget planner
- AI suggestions

User Question:
{user_message}

Context:
{spending_context}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "Finance web app assistant. Line-by-line answers only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        reply = response.choices[0].message.content

        return jsonify({"reply": reply})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"reply": "AI not working. Check API key."})