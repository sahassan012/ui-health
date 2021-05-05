from datetime import datetime, timedelta
import random
from faker import Faker
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from website.models import User, Nurse, Patient, NurseSchedule, AllNursesScheduleTracker, NurseScheduleTracker, \
    Appointment, Vaccine
from website import db

fake_data = Faker()
now = datetime.now()
now_str = str(now.hour) + str(now.second) + str(now.microsecond)
Faker.seed(int(now_str))

sexes = ['Male', 'Female']
races = ['American Indian or Alaska Native', 'Asian', 'Black or African American', 'Hispanic or Latino',
         'Native Hawaiian or Other Pacific Islander', 'White']
occupation_classes = ['Class 5A', 'Class 4P', 'Class 4A', 'Class 3P Surgeon', 'Class 3P', 'Class 3A', 'Class 2P',
                      'Class 2A', 'Class A', 'Class B', 'Unemployed', 'Retired', 'Retail', 'Business Owner', 'Student']
medical_history_types = ['None', 'Pregnant', 'Heart Disease', 'Diabetic', 'Lung cancer', 'Dementia', 'Shrimp Allergy']
email_domains = ['gmail.com', 'yahoo.com', 'sbcglobal.net', 'aol.com', 'msn.com', 'comcast.net', 'mail.ru',
                 'outlook.com']
vaccine_types = ['moderna', 'pfizer', 'johnson']


def insert_admin_login_data():
    new_user = User(email='admin', first_name='Admin',
                    password=generate_password_hash('password', method='sha256'), is_admin=True)
    db.session.add(new_user)
    db.session.commit()


def insert_patient_test_data(add_patient_count):
    for i in range(0, add_patient_count):
        first_name, last_name = fake_data.name().split(' ', 1)
        mi_name = fake_data.name().split(' ', 1)[0]
        last_name = last_name.replace(' ', '')
        first_intial = first_name[0]
        username = (first_intial + last_name.replace('\'', '') + str(random.randrange(0, 500, 1))).lower()
        email = username + '@' + random.choice(email_domains)
        ssn = int(fake_data.ssn().replace('-', ''))
        age = random.randrange(0, 100, 1)
        sex = random.choice(sexes)
        race = random.choice(races)
        occupation_class = random.choice(occupation_classes)
        medical_history = random.choice(medical_history_types)
        phone_number = fake_data.phone_number() \
                           .replace('.', '') \
                           .replace('-', '') \
                           .replace('(', '') \
                           .replace(')', '') \
                           .replace('+', '')[:10]
        address = fake_data.address().replace('\n', ' ')
        user = User(email=email, first_name=first_name, password=generate_password_hash('password', method='sha256'),
                    is_admin=False, is_patient=True, is_nurse=False)
        db.session.add(user)
        db.session.commit()
        patient = Patient(patientID=user.id, username=username, first_name=first_name, mi_name=mi_name,
                          last_name=last_name, SSN=ssn,
                          age=age, sex=sex, race=race, occupation_class=occupation_class,
                          medical_history_description=medical_history, phone_number=phone_number,
                          address=address)
        db.session.add(patient)
        db.session.commit()


def insert_nurse_test_data(add_nurse_count):
    for i in range(0, add_nurse_count):
        first_name, last_name = fake_data.name().split(' ', 1)
        last_name = last_name.replace(' ', '')
        first_intial = first_name[0]
        username = (first_intial + last_name.replace('\'', '') + str(random.randrange(0, 999, 1))).lower()
        email = username + '@uih.com'
        age = random.randrange(20, 55, 1)
        sex = random.choice(sexes)
        phone_number = fake_data.phone_number() \
                           .replace('.', '') \
                           .replace('-', '') \
                           .replace('(', '') \
                           .replace(')', '') \
                           .replace('+', '')[:10]
        address = fake_data.address().replace('\n', ' ')
        user = User(email=email, first_name=first_name, password=generate_password_hash('password', method='sha256'),
                    is_admin=False, is_patient=False, is_nurse=True)
        db.session.add(user)
        db.session.commit()
        nurse = Nurse(employeeID=user.id, email=email, username=username, sex=sex, name=first_name, age=age,
                      phoneNumber=phone_number, address=address)
        db.session.add(nurse)
        db.session.commit()


def insert_schedules_for_existing_nurses():
    """
    Schedule existing nurses for every timeslot starting from two hours from current datetime to 14 days from now.
    """
    start_date = datetime.now() + timedelta(hours=1)
    end_date = start_date + timedelta(days=6)
    nurses = Nurse.query.all()
    num_nurses = len(nurses)
    max_nurses_per_timeslot = 12
    i = 0
    while start_date <= end_date:
        date_timeslot_str = str(start_date)[:14] + '00'
        start_time = datetime.strptime(date_timeslot_str, "%Y-%m-%d %H:00")
        end_time = start_time + timedelta(hours=8)
        while i < max_nurses_per_timeslot:
            schedule = NurseSchedule(nurseID=nurses[i].employeeID, start_time=start_time, end_time=end_time)
            db.session.add(schedule)
            add_to_schedule_tracker(start_time=start_time, end_time=end_time, nurseID=nurses[i].employeeID)
            db.session.commit()
            i += 1
            if i >= num_nurses:
                return
        max_nurses_per_timeslot += 12
        start_date += timedelta(hours=9)


def insert_appointments_for_existing_patients():
    start_date = datetime.now() + timedelta(hours=1)
    end_date = start_date + timedelta(days=6)
    patients = Patient.query.all()
    nurses = Nurse.query.all()
    max_appointments_per_timeslot = 10
    num_patients = len(patients)
    num_nurses = len(nurses)
    n_index = 0
    p_index = 0
    i = 0
    while start_date <= end_date:
        while i < max_appointments_per_timeslot:
            appointment_time = start_date.strftime("%Y-%m-%d %H:00")
            appt = Appointment(appointment_time=appointment_time, nurseID=nurses[n_index].employeeID,
                               patientID=patients[i].patientID,
                               vaccine_type=random.choice(vaccine_types))
            db.session.add(appt)
            db.session.commit()
            i += 1
            if n_index >= num_nurses or i >= num_patients:
                return
        max_appointments_per_timeslot += 10
        p_index += 10
        n_index += 1
        start_date += timedelta(hours=1)


def insert_vaccines():
    moderna_vaccine = Vaccine(name='moderna', company_name='moderna', num_doses=500, description='',
                              num_on_hold=0, num_doses_required=2)
    pfizer_vaccine = Vaccine(name='pfizer', company_name='pfizer', num_doses=500, description='',
                             num_on_hold=0, num_doses_required=2)
    johnson_vaccine = Vaccine(name='johnson', company_name='johnson', num_doses=500, description='',
                              num_on_hold=0, num_doses_required=2)
    db.session.add(moderna_vaccine)
    db.session.add(pfizer_vaccine)
    db.session.add(johnson_vaccine)
    db.session.commit()


def add_to_schedule_tracker(start_time, end_time, nurseID):
    time_slots = []
    while start_time <= end_time:
        start_datetime_str = start_time.strftime("%Y-%m-%d %H:00")
        time_slot = AllNursesScheduleTracker.query.filter_by(timestamp=start_datetime_str).first()
        if time_slot:
            time_slots.append(time_slot)
        else:
            new_time_slot = AllNursesScheduleTracker(timestamp=start_datetime_str, count=0)
            db.session.add(new_time_slot)
            time_slots.append(new_time_slot)
        individual_time_slot = NurseScheduleTracker(nurseID=nurseID, timestamp=start_datetime_str)
        db.session.add(individual_time_slot)
        start_time += timedelta(hours=1)
    for time_slot in time_slots:
        time_slot.count += 1
    db.session.commit()
