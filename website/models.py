from . import db
from flask_login import UserMixin


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
    username = db.Column(db.String(50), unique=True)
    sex = db.Column(db.String(15))
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
    sex = db.Column(db.String(150))
    race = db.Column(db.String(150))
    occupation_class = db.Column(db.String(150))
    medical_history_description = db.Column(db.String(300))
    phone_number = db.Column(db.String(150))
    address = db.Column(db.String(200))


class NurseSchedule(db.Model, UserMixin):
    scheduleID = db.Column(db.Integer, primary_key=True)
    nurseID = db.Column(db.Integer)
    start_time = db.Column(db.DateTime())
    end_time = db.Column(db.DateTime())
    status = db.Column(db.String(10))


class NurseScheduleTracker(db.Model):
    timeslotID = db.Column(db.Integer, primary_key=True)
    nurseID = db.Column(db.Integer)
    timestamp = db.Column(db.String(35))


class AllNursesScheduleTracker(db.Model):
    timestamp = db.Column(db.String(35), primary_key=True)
    count = db.Column(db.Integer)


class Appointment(db.Model, UserMixin):
    appointmentID = db.Column(db.Integer, primary_key=True)
    nurseID = db.Column(db.Integer)
    patientID = db.Column(db.Integer)
    appointment_time = db.Column(db.String(35))
    nurse_comment = db.Column(db.String(150))
    vaccine_type = db.Column(db.String(20))


class Vaccine(db.Model, UserMixin):
    vaccineID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    company_name = db.Column(db.String(20))
    num_doses = db.Column(db.Integer)
    description = db.Column(db.String(150))
    num_on_hold = db.Column(db.Integer)
    num_doses_required = db.Column(db.Integer)


class VaccinationRecord(db.Model, UserMixin):
    vaccinationID = db.Column(db.Integer, primary_key=True)
    patientID = db.Column(db.Integer)
    nurseID = db.Column(db.Integer)
    vaccineID = db.Column(db.Integer)
    scheduled_time = db.Column(db.String(35))
    completed = db.Column(db.Boolean)
