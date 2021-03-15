from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    is_admin = db.Column(db.Boolean, default=False)
    is_patient = db.Column(db.Boolean, default=False)
    is_nurse = db.Column(db.Boolean, default=False)

class Nurse(db.Model, UserMixin):
    employeeID = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150))
    gender = db.Column(db.String(150))
    name = db.Column(db.String(150))
    age = db.Column(db.Integer)
    phoneNumber = db.Column(db.String(150))
    address = db.Column(db.String(200))