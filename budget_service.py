from datetime import datetime
from sqlalchemy import func
from extensions import db
from models import Budget, Transaction, BudgetAlert

CATEGORIES = [
    "ATM Withdrawal",
    "Bills & Utilities",
    "Entertainment",
    "Food & Dining",
    "Groceries",
    "Health",
    "Investment",
    "Shopping",
    "Subscription",
    "Transfer",
    "Travel",
    "Education",
    "Recharge",
    "Uncategorized"
]


# ================= CREATE OR UPDATE BUDGET =================
def create_or_update_budget(user_id, category, monthly_budget, month, year):

    budget = Budget.query.filter_by(
        user_id=user_id,
        category=category,
        month=month,
        year=year
    ).first()

    if budget:
        budget.monthly_budget = monthly_budget
    else:
        budget = Budget(
            user_id=user_id,
            category=category,
            monthly_budget=monthly_budget,
            month=month,
            year=year
        )
        db.session.add(budget)

    db.session.commit()

    return budget


# ================= GET USER BUDGETS =================
def get_user_budgets(user_id, month, year):

    budgets = Budget.query.filter_by(
        user_id=user_id,
        month=month,
        year=year
    ).all()

    budget_dict = {b.category: b for b in budgets}

    all_budgets = []

    for category in CATEGORIES:

        if category in budget_dict:
            all_budgets.append(budget_dict[category])
        else:
            all_budgets.append(
                Budget(
                    user_id=user_id,
                    category=category,
                    monthly_budget=0,
                    month=month,
                    year=year
                )
            )

    return all_budgets


# ================= CALCULATE CATEGORY SPENDING =================
def calculate_category_spending(user_id, category, month, year):

    spent = db.session.query(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).filter(
        Transaction.user_id == user_id,
       func.lower(Transaction.category) == category.lower(),
       func.strftime("%m",Transaction.date) == str(month).zfill(2),
       func.strftime("%Y" , Transaction.date) == str(year)
    ).scalar()

    return spent or 0


# ================= BUDGET ANALYSIS =================
def get_budget_analysis(user_id, month=None, year=None):

    if not month:
        month = datetime.utcnow().month

    if not year:
        year = datetime.utcnow().year

    budgets = get_user_budgets(user_id, month, year)

    analysis = []

    for budget in budgets:

        spent = calculate_category_spending(
            user_id,
            budget.category,
            month,
            year
        )

        remaining = budget.monthly_budget - spent

        percent_used = 0
        if budget.monthly_budget > 0:
            percent_used = round((spent / budget.monthly_budget) * 100, 2)

        analysis.append({
            "category": budget.category,
            "budget": budget.monthly_budget,
            "spent": spent,
            "remaining": remaining,
            "percent_used": percent_used
        })

    return analysis


# ================= GENERATE BUDGET ALERTS =================
def generate_budget_alerts(user_id, analysis):

    alerts = []

    for item in analysis:

        percent = item["percent_used"]

        if percent >= 100:
            message = f"{item['category']} budget exceeded"

        elif percent >= 90:
            message = f"{item['category']} budget almost finished"

        elif percent >= 75:
            message = f"{item['category']} budget 75% used"

        else:
            continue

        alert = BudgetAlert(
            user_id=user_id,
            category=item["category"],
            message=message
        )

        db.session.add(alert)

        alerts.append(message)

    db.session.commit()

    return alerts


# ================= TOTAL BUDGET SUMMARY =================
def get_total_budget_summary(user_id, month=None, year=None):

    if not month:
        month = datetime.utcnow().month

    if not year:
        year = datetime.utcnow().year

    total_budget = db.session.query(
        func.sum(Budget.monthly_budget)
    ).filter(
        Budget.user_id == user_id,
        Budget.month == month,
        Budget.year == year
    ).scalar() or 0

    total_spent = db.session.query(
        func.sum(Transaction.debit)
    ).filter(
        Transaction.user_id == user_id,
        func.strftime("%m" , Transaction.date) == str(month).zfill(2),
        func.strftime("%Y" , Transaction.date) == str(year)
    ).scalar() or 0

    remaining = total_budget - total_spent

    return {
        "total_budget": total_budget,
        "total_spent": total_spent,
        "remaining": remaining
    }


# ================= DAILY SAFE SPENDING =================
def calculate_daily_spending_limit(user_id):

    today = datetime.utcnow()
    month = today.month
    year = today.year

    summary = get_total_budget_summary(user_id, month, year)

    remaining_budget = summary["remaining"]

    days_in_month = 30
    days_passed = today.day

    days_left = max(days_in_month - days_passed, 1)

    daily_limit = remaining_budget / days_left

    return round(daily_limit, 2)