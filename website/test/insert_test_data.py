import random
from faker import Faker
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

from website.models import User, Nurse, Patient
from website import db

fake_data = Faker()

sexes = ['Male', 'Female']
races = ['American Indian or Alaska Native', 'Asian', 'Black or African American', 'Hispanic or Latino',
         'Native Hawaiian or Other Pacific Islander', 'White']
occupation_classes = ['Class 5A', 'Class 4P', 'Class 4A', 'Class 3P Surgeon', 'Class 3P', 'Class 3A', 'Class 2P',
                      'Class 2A', 'Class A', 'Class B', 'Unemployed', 'Retired', 'Retail', 'Business Owner', 'Student']
medical_history_types = ['None', 'Pregnant', 'Heart Disease', 'Diabetic', 'Lung cancer', 'Dementia', 'Shrimp Allergy']
email_domains = ['gmail.com', 'yahoo.com', 'sbcglobal.net', 'aol.com', 'msn.com', 'comcast.net', 'mail.ru',
                 'outlook.com']


def insert_patient_test_data(add_patient_count):
    for i in range(0, add_patient_count):
        first_name, last_name = fake_data.name().split(' ', 1)
        mi_name = fake_data.name().split(' ', 1)[0]
        last_name = last_name.replace(' ', '')
        first_intial = first_name[0]
        username = (first_intial + last_name.replace('\'', '') + str(random.randrange(0, 100, 1))).lower()
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
        patient = Patient(patientID=user.id, username=username, first_name=first_name, mi_name=mi_name, last_name=last_name, SSN=ssn,
                          age=age, sex=sex, race=race, occupation_class=occupation_class, medical_history_description=medical_history, phone_number=phone_number,
                          address=address)
        db.session.add(patient)
        db.session.commit()


def insert_nurse_test_data(add_nurse_count):
    for i in range(0, add_nurse_count):
        first_name, last_name = fake_data.name().split(' ', 1)
        last_name = last_name.replace(' ', '')
        first_intial = first_name[0]
        username = (first_intial + last_name.replace('\'', '') + str(random.randrange(0, 100, 1))).lower()
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
        nurse = Nurse(employeeID=user.id, email=email, username=username, sex=sex,name=first_name, age=age,
                       phoneNumber=phone_number, address=address)
        db.session.add(nurse)
        db.session.commit()

