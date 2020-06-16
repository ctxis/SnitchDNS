import os
import datetime
from flask import Flask, session, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_required, current_user
from flask_crontab import Crontab

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
csrf = CSRFProtect()
crontab = Crontab()


def create_app(config_class=None):
    from app.lib.base.provider import Provider
    provider = Provider()

    # Make sure the instance path is within the ./data folder.
    data_instance_path = os.path.realpath(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data', 'instance'))

    app = Flask(__name__, instance_path=data_instance_path, instance_relative_config=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    dbms = provider.env('SNITCHDNS_DBMS', default='sqlite').lower()
    dbms_uri = ''

    # First we load everything we need in order to end up with a working app.
    if dbms == 'sqlite':
        dbms_uri = 'sqlite:///' + os.path.join(app.instance_path, 'snitchdns.sqlite3')
    elif dbms == 'postgres':
        dbms_uri = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(
            user=provider.env('SNITCHDNS_DB_USER', must_exist=True),
            pw=provider.env('SNITCHDNS_DB_PW', must_exist=True),
            url=provider.env('SNITCHDNS_DB_URL', must_exist=True),
            db=provider.env('SNITCHDNS_DB_DB', must_exist=True)
        )
    elif dbms == 'mysql':
        dbms_uri = 'mysql+pymysql://{user}:{pw}@{url}/{db}'.format(
            user=provider.env('SNITCHDNS_DB_USER', must_exist=True),
            pw=provider.env('SNITCHDNS_DB_PW', must_exist=True),
            url=provider.env('SNITCHDNS_DB_URL', must_exist=True),
            db=provider.env('SNITCHDNS_DB_DB', must_exist=True)
        )
    else:
        raise Exception("Unknown DBMS: {0}".format(dbms))

    app.config['SQLALCHEMY_DATABASE_URI'] = dbms_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SQLALCHEMY_ECHO'] = True
    app.config['SECRET_KEY'] = 'SnitchesGetStitches_:)'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    # This is to ensure only a single cron job runs at a time.
    app.config['CRONTAB_LOCK_JOBS'] = True

    # And now we override any custom settings from config.py if it exists.
    app.config.from_pyfile('config.py', silent=True)

    # If we have passed any object on app creation (ie testing), override here.
    if config_class is not None:
        app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)
    crontab.init_app(app)

    from app.controllers.home import bp as home_bp
    app.register_blueprint(home_bp)

    from app.controllers.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.controllers.dns import bp as dns_bp
    app.register_blueprint(dns_bp)

    from app.controllers.config import bp as config_bp
    app.register_blueprint(config_bp)

    from app.controllers.logs import bp as log_bp
    app.register_blueprint(log_bp)

    from app.controllers.install import bp as install_bp
    app.register_blueprint(install_bp)

    from app.controllers.api import bp as api_bp
    app.register_blueprint(api_bp)
    csrf.exempt(api_bp)

    from app.controllers.notifications import bp as notifications_bp
    app.register_blueprint(notifications_bp)

    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = datetime.timedelta(minutes=20)
        session.modified = True

    @app.after_request
    def after_request(response):
        response.headers['Server'] = 'SnitchesGetStitches'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    @app.context_processor
    def processor():
        def setting_get(name, default=None):
            provider = Provider()
            return provider.settings().get(name, default)

        def is_daemon_running():
            return Provider().daemon().is_running()

        def zone_exists(id=None, full_domain=None):
            return Provider().dns_zones().exists(dns_zone_id=id, full_domain=full_domain)

        return dict(setting_get=setting_get, is_daemon_running=is_daemon_running, zone_exists=zone_exists)

    @app.errorhandler(404)
    @login_required
    def error_handler_404(error):
        # Added the @login_required so that remote enumeration of endpoints won't work.
        # Not that it makes any difference as this is open source. WHAT A TWIST OF THE PLOT.
        return render_template('errors/404.html', error=error), 404

    @app.errorhandler(Exception)
    def error_handler_500(error):
        import traceback
        user_id = current_user.id if current_user.is_authenticated else 0
        Provider().logging().log_error(user_id, str(error), str(traceback.format_exc()))
        return render_template('errors/500.html', error=error, trace=traceback.format_exc()), 500

    # Setup command line.
    from app.lib.cli import env, snitch_daemon, settings, cron, snitchdb
    app.cli.add_command(env.main)
    app.cli.add_command(snitch_daemon.main)
    app.cli.add_command(snitch_daemon.snitch_start)
    app.cli.add_command(settings.main)
    app.cli.add_command(cron.main)
    app.cli.add_command(snitchdb.main)

    # Setup cron job.
    @crontab.job(minute="*/1")
    def cron():
        cron = Provider().cron()
        return cron.run()

    return app

from app.lib.models import user, config, dns, api, notifications, logging
