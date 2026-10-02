from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models.case import Case


main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/dashboard")
@login_required
def dashboard():

    cases_count = Case.query.filter_by(
        user_id=current_user.id
    ).count()

    return render_template(
        "dashboard.html",
        user=current_user,
        cases_count=cases_count
    )
