import click
import sqlalchemy
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import os
import time

from sqlalchemy.exc import InvalidRequestError

db = SQLAlchemy()
DB_NAME = "database.db"
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


def start_app():
    default = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.system("flake8")
    os.chdir(default)
    app.config['SECRET_KEY'] = 'CS480-Project'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_NAME
    db.init_app(app)
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    from .models import User
    create_database(app)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME) and not path.exists(
            os.path.dirname(os.path.abspath(__file__)) + "\\" + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')


@app.cli.command()
def delete_day_old_schedules():
    """Remove all nurse schedules > 1 day old."""
    from .services import remove_inactive_schedules
    print("Removing inactive schedules...")
    remove_inactive_schedules()
    print("Done!")


@app.cli.command()
@click.option('--records')
def create_patients_data(records):
    """Insert patients test data into database.
         'flask create-patients-data --records <# of records>'
       To insert 10 records, use:
         'flask create-patients-data'
    """
    num_new_data = 10
    if records is not None:
        num_new_data = int(records)
    from website.test.insert_test_data import insert_patient_test_data
    insert_patient_test_data(num_new_data)


@app.cli.command()
@click.option('--records')
def create_nurses_data(records):
    """Insert nurses test data into database.
         'flask create-nurses-data --records <# of records>'
       To insert 10 records, use:
         'flask create-nurses-data'
    """
    num_new_data = 10
    if records is not None:
        num_new_data = int(records)
    from website.test.insert_test_data import insert_nurse_test_data
    insert_nurse_test_data(num_new_data)


@app.cli.command()
def insert_nurse_schedules():
    """Insert nurses schedules test data into database.
         'flask insert-nurse-schedules'
    """
    from website.test.insert_test_data import insert_schedules_for_existing_nurses
    insert_schedules_for_existing_nurses()


@app.cli.command()
def insert_appointments():
    """Insert appointments test data into database.
         'flask insert-appointments'
    """
    from website.test.insert_test_data import insert_appointments_for_existing_patients
    insert_appointments_for_existing_patients()


@app.cli.command()
def insert_vaccination_records():
    """Insert vaccination records test data into database.
         'flask insert-vaccination-records'
    """
    from website.test.insert_test_data import insert_vaccination_records_for_existing_patients
    insert_vaccination_records_for_existing_patients()


@app.cli.command()
def create_full_profile_database():
    """Insert all test data into database.
         'flask create-full-profile-database'
    """
    from website.test.insert_test_data import insert_patient_test_data, insert_nurse_test_data, \
        insert_schedules_for_existing_nurses, insert_admin_login_data, \
        insert_appointments_for_existing_patients, insert_vaccines, \
        erase_database, insert_vaccination_records_for_existing_patients
    import os
    clear = lambda: os.system('cls')
    clear()
    print("Creating test data for UI-Health Database...\n")

    erase_database()
    time.sleep(1.0)
    printProgressBar(0, 100, prefix='Progress:', suffix='Deleting current database data...     ', length=30)

    insert_admin_login_data()
    printProgressBar(1, 100, prefix='Progress:', suffix='Admin account is being created...     ', length=30)

    insert_patient_test_data(100)
    printProgressBar(8, 100, prefix='Progress:', suffix='Patients are signing up...         ', length=30)
    insert_patient_test_data(100)
    printProgressBar(16, 100, prefix='Progress:', suffix='Patients are signing up...         ', length=30)
    insert_patient_test_data(100)
    printProgressBar(24, 100, prefix='Progress:', suffix='Patients are signing up...         ', length=30)
    insert_patient_test_data(100)
    printProgressBar(32, 100, prefix='Progress:', suffix='Patients are signing up...         ', length=30)
    insert_patient_test_data(100)
    printProgressBar(40, 100, prefix='Progress:', suffix='Patients are signing up...         ', length=30)
    time.sleep(1.00)

    insert_vaccines()
    printProgressBar(55, 100, prefix='Progress:', suffix='Vaccine inventory is being updated...     ', length=30)

    insert_nurse_test_data(100)
    printProgressBar(60, 100, prefix='Progress:', suffix='Nurses are being registered...          ', length=30)
    insert_nurse_test_data(100)
    printProgressBar(65, 100, prefix='Progress:', suffix='Nurses are being registered...          ', length=30)
    insert_nurse_test_data(100)
    printProgressBar(70, 100, prefix='Progress:', suffix='Nurses are being registered...          ', length=30)
    insert_nurse_test_data(100)
    printProgressBar(75, 100, prefix='Progress:', suffix='Nurses are being registered...          ', length=30)
    insert_nurse_test_data(100)
    printProgressBar(80, 100, prefix='Progress:', suffix='Nurses are being registered...          ', length=30)

    insert_schedules_for_existing_nurses()
    printProgressBar(90, 100, prefix='Progress:', suffix='Nurses are getting scheduled...     ', length=30)

    insert_vaccination_records_for_existing_patients()
    printProgressBar(92, 100, prefix='Progress:', suffix='Storing patient vaccination records...     ', length=30)

    insert_appointments_for_existing_patients()
    printProgressBar(94, 100, prefix='Progress:', suffix='Patients are making appointments...     ', length=30)

    printProgressBar(100, 100, prefix='Progress:', suffix='Complete                                        ', length=30)
    print('\nUI-Health Database successfully created.')


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    source: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    if iteration == total:
        print()
