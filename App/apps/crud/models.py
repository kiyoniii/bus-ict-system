from datetime import datetime
from apps.app import db


class Bus(db.Model):
    __tablename__ = "bus"
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.Integer)
    operation_status = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.now)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    is_on = db.Column(db.Boolean, default=False)
