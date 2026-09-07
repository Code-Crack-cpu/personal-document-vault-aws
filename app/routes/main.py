from functools import wraps

from flask import Blueprint, redirect, render_template, session, url_for

from app.models.document import categories_for_user, recent_for_user

main_bp = Blueprint("main", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


@main_bp.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    categories = categories_for_user(session["user_id"])
    recent = recent_for_user(session["user_id"])
    return render_template(
        "dashboard.html",
        categories=categories,
        recent=recent,
        total_documents=sum(item["total"] for item in categories),
    )
