from flask import Flask, request
import dash
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_babel import Babel
import os
from flask_login import LoginManager
from flask_session import Session
from ccmmdb.core.cli import createdb_command
from werkzeug.middleware.proxy_fix import ProxyFix
from ccmmdb.core.db import db
from ccmmdb.core.csrf import csrf
from ccmmdb.models.models import User




def create_app(config_file=None):
    """Factory to create the Flask application
    :param config_file: A python file from which to load the config.
                        If omitted, the config file must be set using
                        the ``CCMMDB_CONFIG`` environment variable.
                        If set, the environment variable is ignored
    :return: A `Flask` application instance
    """
    app = Flask(__name__)
    _load_config(app, config_file)
    _setup_extentions(app)
    _register_babel(app)
    _register_blueprints(app)
    _setup_db(app)
    _register_graphapp(app)
    _register_predictapp(app)
    _register_handlers(app)
    _setup_login(app)
    app.wsgi_app = ProxyFix(app.wsgi_app, num_proxies=1)

    Bootstrap(app) #TODO: Change to updated version of Bootstrap-Flask
    Migrate(app, db)

    return app


def _setup_db(app):
    # these settings should not be configurable in the config file so we
    # set them after loading the config file
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False
    basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data', 'app.db') + '?check_same_thread=False'
    # ensure all models are imported even if not referenced from already-imported modules
    #import_all_models(app.import_name) # TODO: Get this working
    db.init_app(app)
    with app.app_context():
        db.create_all()



def _load_config(app, config_file):
    app.config.from_pyfile('defaults.cfg')
    if config_file:
        app.config.from_pyfile(config_file)
    elif os.environ.get('CCMMDB_CONFIG') is not None:
       app.config.from_envvar('CCMMDB_CONFIG')
    else:
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
        app.config['CCMM_MEMBERS'] = os.environ.get('CCMM_MEMBERS').split() #This could be a list contained in a string
        app.config['ADMIN_MEMBERS'] = os.environ.get('ADMIN_MEMBERS').split() #This could be a list contained in a string
        app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID')
        app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET')
        app.config['GOOGLE_DISCOVERY_URL'] = os.environ.get('GOOGLE_DISCOVERY_URL')
        app.config['SESSION_TYPE'] = os.environ.get('SESSION_TYPE')



def _register_blueprints(app):
    from ccmmdb.blueprints import main_bp, data_bp, auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(data_bp)
    app.register_blueprint(auth_bp)

def _register_handlers(app):
    @app.context_processor
    def inject_template_scope():
        injections = dict()

        def cookies_check():
            value = request.cookies.get('cookie_consent')
            return value == 'true'

        injections.update(cookies_check=cookies_check)

        return injections


def _setup_extentions(app):
    csrf.init_app(app)
    csrf._exempt_views.add('dash.dash.dispatch')


def _register_graphapp(app):
    from ccmmdb.core.dashapp.graph_layout import layout
    from ccmmdb.core.dashapp.graph_callbacks import register_callbacks

    graphapp = dash.Dash(__name__, url_base_pathname='/graphapp/', server=app, suppress_callback_exceptions=True)

    graphapp.scripts.config.serve_locally = True
    graphapp.css.config.serve_locally = True

    with app.app_context():
        graphapp.layout = layout
        register_callbacks(graphapp)

    return graphapp

def _register_predictapp(app):
    from ccmmdb.core.dashapp.predict_layout import layout
    from ccmmdb.core.dashapp.predict_callbacks import register_callbacks

    predictapp = dash.Dash(__name__, url_base_pathname='/predictapp/', server=app, suppress_callback_exceptions=True)

    predictapp.scripts.config.serve_locally = True
    predictapp.css.config.serve_locally = True

    with app.app_context():
        predictapp.layout = layout
        register_callbacks(predictapp)

    return predictapp

def _register_babel(app):
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'
    babel= Babel()
    babel.init_app(app)

def _setup_login(app):
    Session(app)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.session_protection = "strong"
    login_manager.init_app(app)


    @login_manager.user_loader
    def load_user(user_id):
        u = User.query.filter_by(id=user_id).first()
        if not id:
            return None
        return u






