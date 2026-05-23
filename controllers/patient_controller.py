from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from database import db
from models import Patient, Consulta

patient_bp = Blueprint("patient", __name__, template_folder="../templates")

@patient_bp.route("/", methods=["GET"])
@login_required
def index():
    pacientes = Patient.query.order_by(Patient.nombre).all()
    return render_template("pacientes/index.html", pacientes=pacientes)

@patient_bp.route("/crear", methods=["GET", "POST"])
@login_required
def crear():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        edad = request.form.get("edad", "").strip()
        direccion = request.form.get("direccion", "").strip()
        telefono = request.form.get("telefono", "").strip()

        if not nombre or not edad or not direccion or not telefono:
            flash("Todos los campos son obligatorios.", "warning")
            return render_template("pacientes/create.html")

        try:
            edad = int(edad)
        except ValueError:
            flash("La edad debe ser un número.", "warning")
            return render_template("pacientes/create.html")

        paciente = Patient(nombre=nombre, edad=edad, direccion=direccion, telefono=telefono)
        db.session.add(paciente)
        db.session.commit()
        flash("Paciente registrado.", "success")
        return redirect(url_for("patient.index"))

    return render_template("pacientes/create.html")

@patient_bp.route("/editar/<int:patient_id>", methods=["GET", "POST"])
@login_required
def editar(patient_id):
    paciente = Patient.query.get_or_404(patient_id)
    if request.method == "POST":
        paciente.nombre = request.form.get("nombre", paciente.nombre).strip()
        paciente.edad = request.form.get("edad", paciente.edad)
        paciente.direccion = request.form.get("direccion", paciente.direccion).strip()
        paciente.telefono = request.form.get("telefono", paciente.telefono).strip()

        if not paciente.nombre or not paciente.edad or not paciente.direccion or not paciente.telefono:
            flash("Todos los campos son obligatorios.", "warning")
            return render_template("pacientes/edit.html", paciente=paciente)

        try:
            paciente.edad = int(paciente.edad)
        except ValueError:
            flash("La edad debe ser un número.", "warning")
            return render_template("pacientes/edit.html", paciente=paciente)

        db.session.commit()
        flash("Datos del paciente actualizados.", "success")
        return redirect(url_for("patient.index"))

    return render_template("pacientes/edit.html", paciente=paciente)

@patient_bp.route("/eliminar/<int:patient_id>")
@login_required
def eliminar(patient_id):
    paciente = Patient.query.get_or_404(patient_id)
    db.session.delete(paciente)
    db.session.commit()
    flash("Paciente eliminado.", "success")
    return redirect(url_for("patient.index"))

@patient_bp.route("/historial/<int:patient_id>")
@login_required
def historial(patient_id):
    paciente = Patient.query.get_or_404(patient_id)
    consultas = Consulta.query.filter_by(paciente_id=patient_id).order_by(Consulta.fecha.desc()).all()
    return render_template("pacientes/historial.html", paciente=paciente, consultas=consultas)
