from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import db
from models import Doctor

doctor_bp = Blueprint("doctor", __name__, template_folder="../templates")

@doctor_bp.route("/", methods=["GET"])
@login_required
def index():
    doctores = Doctor.query.order_by(Doctor.nombre).all()
    return render_template("doctores/index.html", doctores=doctores)

@doctor_bp.route("/crear", methods=["GET", "POST"])
@login_required
def crear():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        especialidad = request.form.get("especialidad", "").strip()
        telefono = request.form.get("telefono", "").strip()
        correo = request.form.get("correo", "").strip()

        if not nombre or not especialidad or not telefono or not correo:
            flash("Todos los campos son obligatorios.", "warning")
            return render_template("doctores/create.html")

        if Doctor.query.filter_by(correo=correo).first():
            flash("Ya existe un médico con ese correo.", "warning")
            return render_template("doctores/create.html")

        doctor = Doctor(nombre=nombre, especialidad=especialidad, telefono=telefono, correo=correo)
        db.session.add(doctor)
        db.session.commit()
        flash("Médico registrado.", "success")
        return redirect(url_for("doctor.index"))

    return render_template("doctores/create.html")

@doctor_bp.route("/editar/<int:doctor_id>", methods=["GET", "POST"])
@login_required
def editar(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    if request.method == "POST":
        doctor.nombre = request.form.get("nombre", doctor.nombre).strip()
        doctor.especialidad = request.form.get("especialidad", doctor.especialidad).strip()
        doctor.telefono = request.form.get("telefono", doctor.telefono).strip()
        doctor.correo = request.form.get("correo", doctor.correo).strip()

        if not doctor.nombre or not doctor.especialidad or not doctor.telefono or not doctor.correo:
            flash("Todos los campos son obligatorios.", "warning")
            return render_template("doctores/edit.html", doctor=doctor)

        db.session.commit()
        flash("Datos del médico actualizados.", "success")
        return redirect(url_for("doctor.index"))

    return render_template("doctores/edit.html", doctor=doctor)

@doctor_bp.route("/eliminar/<int:doctor_id>")
@login_required
def eliminar(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    db.session.delete(doctor)
    db.session.commit()
    flash("Médico eliminado.", "success")
    return redirect(url_for("doctor.index"))
