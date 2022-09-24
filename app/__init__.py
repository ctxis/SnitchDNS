import os
import datetime
from flask import Flask, session, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_required, current_user
from flask_crontab import Crontab
from app.lib.base.environment import EnvironmentManager
from app import version
from werkzeug.middleware.proxy_fix import ProxyFix

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
csrf = CSRFProtect()
crontab = Crontab()


def create_app(config_class=None):
    from app.lib.base.provider import Provider
    provider = Provider()
    environment = EnvironmentManager()

    # Make sure the instance path is within the ./data folder.
    data_path = environment.get_data_path()
    app = Flask(__name__, instance_path=os.path.join(data_path, 'instance'), instance_relative_config=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    dbms = environment.env('SNITCHDNS_DBMS', default='sqlite').lower()
    dbms_uri = ''

    # First we load everything we need in order to end up with a working app.
    if dbms == 'sqlite':
        dbms_uri = 'sqlite:///' + os.path.join(app.instance_path, 'snitchdns.sqlite3')
    elif dbms in ['mysql', 'postgres']:
        if dbms == 'postgres':
            dbms_uri = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'
        elif dbms == 'mysql':
            dbms_uri = 'mysql+pymysql://{user}:{pw}@{url}/{db}?charset=utf8mb4'

        dbms_uri = dbms_uri.format(
            user=environment.env('SNITCHDNS_DB_USER', must_exist=True),
            pw=environment.env('SNITCHDNS_DB_PW', must_exist=True),
            url=environment.env('SNITCHDNS_DB_URL', must_exist=True),
            db=environment.env('SNITCHDNS_DB_DB', must_exist=True)
        )
    else:
        raise Exception("Unknown DBMS: {0}".format(dbms))

    app.config['SQLALCHEMY_DATABASE_URI'] = dbms_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SQLALCHEMY_ECHO'] = True
    app.config['SECRET_KEY'] = environment.env('SNITCHDNS_SECRET_KEY', must_exist=True)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    # This is to ensure only a single cron job runs at a time.
    app.config['CRONTAB_LOCK_JOBS'] = True
    # The referrer is disabled further down in the response headers.
    app.config['WTF_CSRF_SSL_STRICT'] = False
    app.config['PREFERRED_URL_SCHEME'] = 'https'

    # And now we override any custom settings from config.py if it exists.
    app.config.from_pyfile('config.py', silent=True)

    app.config['SNITCHDNS_VERSION'] = version.__version__

    # If we have passed any object on app creation (ie testing), override here.
    if config_class is not None:
        app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)
    crontab.init_app(app)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

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

        def zone_exists(id=None, domain=None):
            return Provider().dns_zones().exists(dns_zone_id=id, domain=domain)

        def tag_domains(tag_id):
            return Provider().dns_zones().tag_count(tag_id)

        return dict(
            setting_get=setting_get,
            is_daemon_running=is_daemon_running,
            zone_exists=zone_exists,
            tag_domains=tag_domains
        )

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
    from app.lib.cli import env, snitch_daemon, settings, cron, snitchdb, zones, users, records, restrictions
    app.cli.add_command(env.main)
    app.cli.add_command(snitch_daemon.main)
    app.cli.add_command(snitch_daemon.snitch_start)
    app.cli.add_command(settings.main)
    app.cli.add_command(cron.main)
    app.cli.add_command(snitchdb.main)
    app.cli.add_command(users.main)
    app.cli.add_command(zones.main)
    app.cli.add_command(records.main)
    app.cli.add_command(restrictions.main)

    # Setup cron job.
    @crontab.job(minute="*/1")
    def cron():
        cron = Provider().cron()
        return cron.run()

    return app

from app.lib.models import user, config, dns, api, notifications, logging, tags, aliases
