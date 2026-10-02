from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user

from models import db
from models.user import User


auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("аполните все поля.", "error")
            return render_template("login.html")

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash("еверный email или пароль.", "error")
            return render_template("login.html")

        login_user(user)

        return redirect(url_for("main.dashboard"))

    return render_template("login.html")


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")

        if not username or not email or not password or not password_confirm:
            flash("аполните все поля.", "error")
            return render_template("register.html")

        if password != password_confirm:
            flash("ароли не совпадают.", "error")
            return render_template("register.html")

        existing_user = User.query.filter(
            (User.email == email) |
            (User.username == username)
        ).first()

        if existing_user:
            flash(
                "ользователь с таким email или именем уже существует.",
                "error"
            )
            return render_template("register.html")

        user = User(
            username=username,
            email=email
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        login_user(user)

        return redirect(url_for("main.dashboard"))

    return render_template("register.html")


@auth.route("/logout")
def logout():

    logout_user()

    return redirect(url_for("main.index"))
