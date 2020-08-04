import os
from flask import Flask

def create_app() -> Flask:
    app = Flask(__name__)
    config_app(flask_app=app)
    init_views(app)
    return app


def config_app(flask_app: Flask) -> Flask:
    flask_app.logger.info("Starting configuration of Flask-App")
    flask_app.logger.info("Flask App configured.")

    load_default_config_file(flask_app=flask_app)

    flask_app.logger.debug(f"{flask_app.config}")


def load_default_config_file(flask_app: Flask) -> None:
    flask_app.logger.info("Starting default configuration")

    flask_app.config.from_object('config.default')

    flask_app.logger.info("Loaded config defaults for all environments.")
    flask_app.logger.debug(f"{flask_app.config}")


def init_views(flask_app: Flask) -> None:
    flask_app.logger.info("Start initializing views.")

    with flask_app.app_context():
        from nlmapsweb import views

        imported = [v for v in views.__dict__ if not v.startswith('_')]

        flask_app.logger.info("Views initialized.")
        flask_app.logger.debug(f"{', '.join(imported)}")
