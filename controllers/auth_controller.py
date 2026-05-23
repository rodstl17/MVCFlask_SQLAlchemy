from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from database import db
from models import User

auth_bp = Blueprint("auth", __name__, template_folder="../templates")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.panel"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Credenciales inválidas.", "danger")
            return render_template("login.html")

        login_user(user)
        return redirect(url_for("auth.panel"))

    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth.panel"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm = request.form.get("confirm", "").strip()

        if not username or not email or not password or not confirm:
            flash("Todos los campos son obligatorios.", "warning")
            return render_template("register.html")

        if password != confirm:
            flash("Las contraseñas no coinciden.", "warning")
            return render_template("register.html")

        if User.query.filter((User.email == email) | (User.username == username)).first():
            flash("Usuario o correo ya registrado.", "warning")
            return render_template("register.html")

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registro exitoso. Inicia sesión.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Se ha cerrado la sesion.", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/panel")
@login_required
def panel():
    from models import Doctor, Patient, Consulta
    total_doctores = Doctor.query.count()
    total_pacientes = Patient.query.count()
    total_consultas = Consulta.query.count()
    return render_template(
        "dashboard.html",
        total_doctores=total_doctores,
        total_pacientes=total_pacientes,
        total_consultas=total_consultas,
    )
