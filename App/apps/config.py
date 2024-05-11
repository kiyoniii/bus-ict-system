from pathlib import Path
import os

basedir = Path(__file__).parent.parent


class BaseCinfig:
    SECRET_KEY = os.environ['SECRET_KEY']
    WTF_CSRF_SECRET_KEY = os.environ['WTF_CSRF_SECRET_KEY']


class LocalConfig(BaseCinfig):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir/'local.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Falseじゃないとエラーが発生
    SQLALCHEMY_ECHO = True


class ProductConfig(BaseCinfig):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir/'product.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Falseじゃないとエラーが発生
    WTF_CSRF_ENABLED = False  # CSRFを無効にする（対策する）


config = {"local": LocalConfig, "product": ProductConfig}
