import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect


db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()


def create_app(config_class=None):
    app = Flask(__name__, instance_relative_config=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # First we load everything we need in order to end up with a working app.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'snitchdns.sqlite3')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'SnitchesGetStitches_:)'
    app.config['SESSION_COOKIE_HTTPONLY'] = True

    # And now we override any custom settings from config.py if it exists.
    app.config.from_pyfile('config.py', silent=True)

    # If we have passed any object on app creation (ie testing), override here.
    if config_class is not None:
        app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    return app
