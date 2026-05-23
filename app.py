import os
from flask import Flask, redirect, url_for, flash
from flask_login import LoginManager, current_user
from database import db

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Inicia sesión para acceder."


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "clinica-secreta-123")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///clinica.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    from models import User
    from controllers.auth_controller import auth_bp
    from controllers.doctor_controller import doctor_bp
    from controllers.patient_controller import patient_bp
    from controllers.consulta_controller import consulta_bp
    from controllers.report_controller import report_bp

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        if User.query.count() == 0:
            admin = User(username="admin", email="admin@outlook.es", is_admin=True)
            admin.set_password("admin0000")
            db.session.add(admin)
            db.session.commit()

    @app.route("/")
    def home():
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        return redirect(url_for("auth.panel"))

    app.register_blueprint(auth_bp)
    app.register_blueprint(doctor_bp, url_prefix="/doctores")
    app.register_blueprint(patient_bp, url_prefix="/pacientes")
    app.register_blueprint(consulta_bp, url_prefix="/consultas")
    app.register_blueprint(report_bp, url_prefix="/reportes")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
