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
    username = db.Column(db.String(150), unique=True)
    gender = db.Column(db.String(150))
    name = db.Column(db.String(150))
    age = db.Column(db.Integer)
    phoneNumber = db.Column(db.String(150))
    address = db.Column(db.String(200))

class Patient(db.Model, UserMixin):
    patientID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    first_name = db.Column(db.String(150))
    mi_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    SSN = db.Column(db.Integer, unique=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(150))
    race = db.Column(db.String(150))
    occupation_class = db.Column(db.String(150))
    medical_history_description = db.Column(db.String(300))
    phone_number = db.Column(db.String(150))
    address = db.Column(db.String(200))

class Nurse_Schedule(db.Model, UserMixin):
    scheduleID = db.Column(db.Integer, primary_key=True)
    nurseID = db.Column(db.Integer, unique=True)
    date = db.Column(db.DateTime())
    appointment_time = db.Column(db.DateTime())
    status = db.Column(db.String(50))
    nurse_comment = db.Column(db.String(250))