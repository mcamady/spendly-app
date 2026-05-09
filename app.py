import calendar
import sqlite3
from datetime import date, datetime


from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db
from database.queries import (
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
    get_user_by_id,
    insert_expense,
)

app = Flask(__name__)
app.secret_key = "dev-secret-key"

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]

with app.app_context():
    init_db()
    seed_db()


def _parse_date(val):
    try:
        datetime.strptime(val, "%Y-%m-%d")
        return val
    except (ValueError, TypeError):
        return None


def _months_ago(today, n):
    m, y = today.month - n, today.year
    while m <= 0:
        m += 12
        y -= 1
    return date(y, m, 1).isoformat()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not all([name, email, password, confirm_password]):
            flash("All fields are required.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        try:
            create_user(name, email, password)
        except sqlite3.IntegrityError:
            flash("Email already registered.", "error")
            return render_template("register.html")

        flash("Account created! Please sign in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_email(email)
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("profile"))

    return render_template("login.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    # Guard: redirect unauthenticated users
    if not session.get("user_id"):
        return redirect(url_for("login"))

    # Hard‑coded user info
    user = {
        "initials": "JD",
        "name": "Jane Doe",
        "email": "jane@example.com",
        "member_since": "2023-01-15",
    }

    # Hard‑coded summary stats
    stats = {
        "total": "$1,250.00",
        "count": 42,
        "top_category": "Food",
    }

    # Hard‑coded recent expenses
    expenses = [
        {"date": "2026-05-01", "description": "Coffee", "category": "Food", "amount": "$4.50"},
        {"date": "2026-04-28", "description": "Metro ticket", "category": "Transport", "amount": "$2.75"},
        {"date": "2026-04-25", "description": "Internet Bill", "category": "Bills", "amount": "$55.00"},
    ]

    # Hard‑coded category breakdown (percentages for progress bars)
    categories = [
        {"name": "Food", "amount": "$300", "percent": 30},
        {"name": "Transport", "amount": "$120", "percent": 12},
        {"name": "Bills", "amount": "$500", "percent": 50},
    ]

    # Preserve filter presets (same as before) – they are unused in hard‑coded view but kept for consistency
    today = date.today()
    today_str = today.isoformat()
    this_month_from = today.replace(day=1).isoformat()
    this_month_to = today.replace(day=calendar.monthrange(today.year, today.month)[1]).isoformat()
    presets = {
        "this_month": {"date_from": this_month_from, "date_to": this_month_to},
        "last_3": {"date_from": _months_ago(today, 3), "date_to": today_str},
        "last_6": {"date_from": _months_ago(today, 6), "date_to": today_str},
    }

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        expenses=expenses,
        categories=categories,
        date_from=None,
        date_to=None,
        presets=presets,
    )


@app.route("/analytics")
def analytics():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    return render_template("analytics.html")


@app.route("/expenses/add", methods=["GET", "POST"])
def add_expense():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    today = date.today().isoformat()

    if request.method == "POST":
        amount_raw = request.form.get("amount", "").strip()
        category = request.form.get("category", "").strip()
        expense_date = request.form.get("date", "").strip()
        description = request.form.get("description", "").strip()

        try:
            amount = float(amount_raw)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("Amount must be a positive number.", "error")
            return render_template("add_expense.html", categories=CATEGORIES, form=request.form, today=today)

        if category not in CATEGORIES:
            flash("Please select a valid category.", "error")
            return render_template("add_expense.html", categories=CATEGORIES, form=request.form, today=today)

        if not _parse_date(expense_date):
            flash("Please enter a valid date.", "error")
            return render_template("add_expense.html", categories=CATEGORIES, form=request.form, today=today)

        insert_expense(session["user_id"], amount, category, expense_date, description)
        flash("Expense added.", "success")
        return redirect(url_for("profile"))

    return render_template("add_expense.html", categories=CATEGORIES, form={}, today=today)


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
