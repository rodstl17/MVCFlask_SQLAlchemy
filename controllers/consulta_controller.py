from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from database import db
from models import Consulta, Doctor, Patient

consulta_bp = Blueprint("consulta", __name__, template_folder="../templates")

@consulta_bp.route("/", methods=["GET"])
@login_required
def index():
    fecha = request.args.get("fecha", "").strip()
    consultas = Consulta.query.order_by(Consulta.fecha.desc())

    if fecha:
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
            consultas = consultas.filter(db.func.date(Consulta.fecha) == fecha_obj.date())
        except ValueError:
            flash("Formato de fecha inválido. Usa AAAA-MM-DD.", "warning")

    consultas = consultas.all()
    return render_template("consultas/index.html", consultas=consultas, fecha=fecha)

@consulta_bp.route("/crear", methods=["GET", "POST"])
@login_required
def crear():
    doctores = Doctor.query.order_by(Doctor.nombre).all()
    pacientes = Patient.query.order_by(Patient.nombre).all()

    if request.method == "POST":
        fecha = request.form.get("fecha", "").strip()
        medico_id = request.form.get("medico_id", "").strip()
        paciente_id = request.form.get("paciente_id", "").strip()
        diagnostico = request.form.get("diagnostico", "").strip()
        tratamiento = request.form.get("tratamiento", "").strip()
        nota = request.form.get("nota", "").strip()

        if not fecha or not medico_id or not paciente_id or not diagnostico or not tratamiento:
            flash("Todos los campos obligatorios deben completarse.", "warning")
            return render_template("consultas/create.html", doctores=doctores, pacientes=pacientes)

        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash("Fecha y hora inválidas.", "warning")
            return render_template("consultas/create.html", doctores=doctores, pacientes=pacientes)

        consulta = Consulta(
            fecha=fecha_obj,
            medico_id=int(medico_id),
            paciente_id=int(paciente_id),
            diagnostico=diagnostico,
            tratamiento=tratamiento,
            nota=nota or None,
        )
        db.session.add(consulta)
        db.session.commit()
        flash("Consulta registrada.", "success")
        return redirect(url_for("consulta.index"))

    return render_template("consultas/create.html", doctores=doctores, pacientes=pacientes)

@consulta_bp.route("/editar/<int:consulta_id>", methods=["GET", "POST"])
@login_required
def editar(consulta_id):
    consulta = Consulta.query.get_or_404(consulta_id)
    doctores = Doctor.query.order_by(Doctor.nombre).all()
    pacientes = Patient.query.order_by(Patient.nombre).all()

    if request.method == "POST":
        fecha = request.form.get("fecha", "").strip()
        consulta.medico_id = int(request.form.get("medico_id", consulta.medico_id))
        consulta.paciente_id = int(request.form.get("paciente_id", consulta.paciente_id))
        consulta.diagnostico = request.form.get("diagnostico", consulta.diagnostico).strip()
        consulta.tratamiento = request.form.get("tratamiento", consulta.tratamiento).strip()
        consulta.nota = request.form.get("nota", consulta.nota or "").strip() or None

        if not fecha or not consulta.diagnostico or not consulta.tratamiento:
            flash("Todos los campos obligatorios deben completarse.", "warning")
            return render_template("consultas/edit.html", consulta=consulta, doctores=doctores, pacientes=pacientes)

        try:
            consulta.fecha = datetime.strptime(fecha, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash("Fecha y hora inválidas.", "warning")
            return render_template("consultas/edit.html", consulta=consulta, doctores=doctores, pacientes=pacientes)

        db.session.commit()
        flash("Consulta actualizada.", "success")
        return redirect(url_for("consulta.index"))

    return render_template("consultas/edit.html", consulta=consulta, doctores=doctores, pacientes=pacientes)

@consulta_bp.route("/eliminar/<int:consulta_id>")
@login_required
def eliminar(consulta_id):
    consulta = Consulta.query.get_or_404(consulta_id)
    db.session.delete(consulta)
    db.session.commit()
    flash("Consulta eliminada.", "success")
    return redirect(url_for("consulta.index"))
