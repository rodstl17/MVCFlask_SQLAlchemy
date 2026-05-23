import csv
from io import StringIO
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required
from models import Doctor, Patient, Consulta

report_bp = Blueprint("report", __name__, template_folder="../templates")

@report_bp.route("/", methods=["GET"])
@login_required
def index():
    consultas = Consulta.query.order_by(Consulta.fecha.desc()).all()
    total_doctores = Doctor.query.count()
    total_pacientes = Patient.query.count()
    return render_template("reportes/index.html", consultas=consultas, total_doctores=total_doctores, total_pacientes=total_pacientes)

@report_bp.route("/exportar", methods=["GET"])
@login_required
def exportar():
    consultas = Consulta.query.order_by(Consulta.fecha.desc()).all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Fecha", "Médico", "Paciente", "Diagnóstico", "Tratamiento", "Nota"])

    for consulta in consultas:
        writer.writerow([
            consulta.id,
            consulta.fecha.strftime("%Y-%m-%d %H:%M"),
            consulta.doctor.nombre,
            consulta.paciente.nombre,
            consulta.diagnostico,
            consulta.tratamiento,
            consulta.nota or "",
        ])

    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=reportes_consultas.csv"},
    )
