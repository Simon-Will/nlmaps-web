from configparser import ConfigParser
import os
import sys

from flask import Flask
from flask_login import AnonymousUserMixin, LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from nlmaps_web.utils.json import SymbolAwareJSONEncoder
from nlmaps_web.utils.template_filters import FILTERS as JINJA_FILTERS

csrf = CSRFProtect()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app() -> Flask:
    app = Flask(__name__)
    config_app(app)
    init_jinja(app)
    init_csrf(app)
    init_sqlalchemy(app)
    init_migrate(app)
    init_login(app)
    init_views(app)
    import_models()
    init_cli(app)

    app.json_encoder = SymbolAwareJSONEncoder
    return app


def config_app(app: Flask) -> Flask:
    app.logger.info('Start loading config.')
    app.logger.info('Flask App configured.')

    app.logger.info('Loading default configuration.')
    app.config.from_object('nlmaps_web.config.default')
    env = os.environ.get('FLASK_ENV')
    if env:
        try:
            app.logger.info('Loading {} configuration.'.format(env))
            app.config.from_object('nlmaps_web.config.' + env.lower())
        except ImportError:
            app.logger.error('Could not load {} configuration.'.format(env))
            sys.exit(1)

    secrets_ini = app.config.get('SECRETS_INI')
    if secrets_ini:
        app.logger.info('Loading {}.'.format(secrets_ini))
        cp = ConfigParser(delimiters=('=',), comment_prefixes=('#',))
        cp.read(secrets_ini)
        for key, value in cp['DEFAULT'].items():
            app.config[key.upper()] = value


    app.logger.info('Config loaded.')
    app.logger.debug(f'{app.config}')


def init_jinja(app: Flask) -> None:
    app.logger.info('Start initializing Jinja.')
    for func in JINJA_FILTERS:
        app.add_template_filter(func)
    app.logger.info('Jinja initialized.')


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
    login_manager.login_view = 'login'
    login_manager.init_app(app=app)
    from nlmaps_web.models.users import User

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
        from nlmaps_web import views
        imported = [v for v in views.__dict__ if not v.startswith('_')]
        app.logger.info('Views initialized.')


def init_cli(app: Flask) -> None:
    from nlmaps_web.commands import specs
    for spec in specs:
        group = app.cli.group()(spec["group"])
        for command in spec["commands"]:
            group.command()(command)
    app.logger.info("Flask cli commands registered.")


def import_models() -> None:
    import nlmaps_web.models
