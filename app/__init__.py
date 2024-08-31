import os

from flask import Flask
from sqlalchemy import select
from werkzeug.security import generate_password_hash

from config import Config
from .classes.classes import Regions, Roles
from .model.tables import db_session, Users
from .routes.route import bp as route_bp


def create_app(config_class=Config):
    """
    Create and configure the Flask application.

    Parameters:
        config_class: The configuration class to use for the application.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.register_blueprint(route_bp)

    if not os.path.isdir(Config.BASE_PATH):
        os.mkdir(Config.BASE_PATH)
    for region in Regions:
        region_path = os.path.join(Config.BASE_PATH, region.value)
        if not os.path.isdir(region_path):
            os.mkdir(region_path)
        for letter in "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЫЭЮЯ":
            letter_path = os.path.join(region_path, letter)
            if not os.path.isdir(letter_path):
                os.mkdir(letter_path)

    if not db_session.execute(select(Users)).all():
        admin = Users(
            fullname="Администратор",
            username="superadmin",
            role=Roles.admin.value,
            passhash=generate_password_hash(Config.DEFAULT_PASSWORD),
            region=Regions.main.value,
        )
        db_session.add(admin)
        db_session.commit()
        db_session.remove()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    @app.get("/<path:path>")
    def static_file(path=""):
        return app.send_static_file(path)

    @app.errorhandler(404)
    def not_found(error):
        return app.redirect("/")

    return app
