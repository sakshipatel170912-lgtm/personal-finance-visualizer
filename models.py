from extensions import db
from flask_login import UserMixin
from datetime import datetime


# ================= USER MODEL =================
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean , default=False)

    # 🔥 NEW: Preferences
    currency = db.Column(db.String(10), default="INR")
    theme = db.Column(db.String(20), default="light")
    notifications = db.Column(db.Boolean, default=True)

    # ================= RELATIONSHIPS =================
    transactions = db.relationship(
        "Transaction",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    category_rules = db.relationship(
        "CategoryRule",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    budgets = db.relationship(
        "Budget",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    budget_alerts = db.relationship(
        "BudgetAlert",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    # 🔥 NEW: Financial Goals relationship
    financial_goal = db.relationship(
        "FinancialGoal",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )


# ================= TRANSACTION MODEL =================
class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(255), nullable=False)

    amount = db.Column(db.Float, nullable=False)
    debit = db.Column(db.Float, default=0)
    credit = db.Column(db.Float, default=0)

    category = db.Column(db.String(50), default="Uncategorized", index=True)

    batch_id = db.Column(db.String(50), nullable=True, index=True)
    source = db.Column(db.String(20), nullable=False)  # manual / upload

    is_locked = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


# ================= CATEGORY RULE MODEL =================
class CategoryRule(db.Model):
    __tablename__ = "category_rules"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    keyword = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)


# ================= BUDGET MODEL (MODULE 6) =================
class Budget(db.Model):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    category = db.Column(db.String(100), nullable=False)
    monthly_budget = db.Column(db.Float, nullable=False)

    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "category",
            "month",
            "year",
            name="unique_budget_per_category_month"
        ),
    )


# ================= BUDGET ALERT MODEL =================
class BudgetAlert(db.Model):
    __tablename__ = "budget_alerts"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    category = db.Column(db.String(100))
    message = db.Column(db.String(255))

    is_read = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ================= FINANCIAL GOALS MODEL (MODULE 9) =================
class FinancialGoal(db.Model):
    __tablename__ = "financial_goals"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True   # 🔥 One goal per user
    )

    monthly_saving_goal = db.Column(db.Float, nullable=True)
    monthly_budget = db.Column(db.Float, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)