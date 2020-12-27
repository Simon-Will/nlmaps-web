import os

from flask import Flask
from flask_login import AnonymousUserMixin, LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from nlmapsweb.utils.json import SymbolAwareJSONEncoder

csrf = CSRFProtect()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app() -> Flask:
    app = Flask(__name__)
    config_app(app)
    init_csrf(app)
    init_sqlalchemy(app)
    init_migrate(app)
    init_login(app)
    init_views(app)
    import_models()
    init_cli()

    app.json_encoder = SymbolAwareJSONEncoder
    return app


def config_app(app: Flask) -> Flask:
    app.logger.info('Starting configuration of Flask-App.')
    app.logger.info('Flask App configured.')
    load_default_config_file(app=app)
    app.logger.debug(f'{app.config}')


def load_default_config_file(app: Flask) -> None:
    app.logger.info('Loading default configuration.')
    app.config.from_object('config.default')
    app.logger.info('Loaded config defaults for all environments.')
    app.logger.debug(f'{app.config}')

def init_csrf(app: Flask) -> None:
    app.logger.info('Start initializing CSRF protection.')
    csrf.init_app(app=app)
    app.logger.info('CSRF protection initialized.')


def init_sqlalchemy(app: Flask) -> None:
    app.logger.info('Start initializing Flask-SQLAlchemy.')
    db.init_app(app=app)
    app.logger.info('Flask-SQLAlchemy initialized.')


def init_migrate(app: Flask) -> None:
    app.logger.info("Start initializing Flask-Migrate.")
    migrate.init_app(app=app, db=db)
    app.logger.info("Flask-Migrate initialized.")


def init_login(app: Flask) -> None:
    app.logger.info("Start initializing Flask-Login.")
    login_manager.init_app(app=app)
    from nlmapsweb.models.users import User

    @login_manager.user_loader
    def user_loader(id):
        return User.query.get(int(id))

    class AnonymousUser(AnonymousUserMixin):
        @property
        def admin(self):
            return False

    login_manager.anonymous_user = AnonymousUser

    app.logger.info("Flask-Login initialized.")


def init_views(app: Flask) -> None:
    app.logger.info('Start initializing views.')

    with app.app_context():
        from nlmapsweb import views

        imported = [v for v in views.__dict__ if not v.startswith('_')]

        app.logger.info('Views initialized.')


def init_cli(app: Flask) -> None:
    from nlmapsweb.commands import specs
    for spec in specs:
        group = app.cli.group()(spec["group"])
        for command in spec["commands"]:
            group.command()(command)
    app.logger.info("Flask cli commands registered.")


def import_models() -> None:
    import nlmapsweb.models
