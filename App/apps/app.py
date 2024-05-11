from flask import Flask
from apps.config import config
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_key):
    app = Flask(__name__)

    app.config.from_object(config[config_key])
    db.init_app(app)
    Migrate(app, db)

    from apps.notice import views as notice_views

    app.register_blueprint(notice_views.notice, url_prefix="/notice")

    from apps.counting import views as counting_views

    app.register_blueprint(counting_views.counting, url_prefix="/counting")

    return app
