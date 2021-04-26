from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Nurse, User, Patient, NurseSchedule, Vaccine, NurseScheduleTracker, Appointment
from .services import check_schedules_for_conflict, remove_schedule_count, \
    str_to_datetime, str_to_datetime_v2, add_schedule_count, convert_timeslots_to_dictionary
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from . import db
import json
import datetime
from datetime import date, timedelta

views = Blueprint('views', __name__)
DB_NAME = "database.db"

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if current_user.is_admin:
        return render_template("/admin/admin.html", user=current_user)
    return render_template("home.html", user=current_user)


@views.route('/register-nurse')
def register_nurse():
    if current_user.is_anonymous or not current_user.is_authenticated or not current_user.is_admin:
        return render_template("/errors/403.html", user=current_user)
    nurses = Nurse.query.all()
    return render_template("/admin/register_nurse.html", user=current_user, nurses=nurses)


@views.route('/create-nurse', methods=['POST'])
def create_nurse():
    if not current_user.is_admin:
        return render_template("/errors/403.html", user=current_user)
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        gender = request.form['gender']
        name = request.form['name']
        age = request.form['age']
        phoneNumber = request.form['phoneNumber']
        address = request.form['address']

        nurse_username = Nurse.query.filter_by(username=username).first()
        nurse_email = Nurse.query.filter_by(username=email).first()
        if nurse_username:
            flash('Username given already exists.', category='error')
        elif nurse_email:
            flash('Email given already exists.', category='error')
        else:
            user = create_user(email, name, password, is_admin=False, is_patient=False, is_nurse=True)
            if user is None:
                flash('Something went wrong!', category='error')
            else:
                new_nurse = Nurse(employeeID=user.id, email=email, username=username, gender=gender, name=name, age=age,
                                  phoneNumber=phoneNumber, address=address)
                db.session.add(new_nurse)
                db.session.commit()
                flash('Nurse created!', category='success')
        return redirect(url_for('views.register_nurse'))


@views.route('/update-nurse', methods=['GET', 'POST'])
def update_nurse():
    if request.method == 'POST':
        data = Nurse.query.get(request.form.get('employeeID'))
        data.email = request.form['email']
        data.username = request.form['username']
        data.gender = request.form['gender']
        data.name = request.form['name']
        data.age = request.form['age']
        data.phoneNumber = request.form['phoneNumber']
        data.address = request.form['address']
        db.session.commit()
        flash("Nurse updated Sucessfully!")
        return redirect(url_for('views.register_nurse'))


@views.route('/delete-nurse/<id>/', methods=['GET', 'POST'])
def delete_nurse(id):
    data = Nurse.query.get(id)
    db.session.delete(data)
    db.session.commit()
    delete_user(id)
    flash("Nurse Deleted Successfully")
    return redirect(url_for('views.register_nurse'))


def create_user(email, first_name, password, is_admin, is_patient, is_nurse):
    user = User.query.filter_by(email=email).first()
    if user:
        flash('Email already exists.', category='error')
    elif len(email) < 4:
        flash('Email must be greater than 3 characters.', category='error')
    elif len(first_name) < 2:
        flash('First name must be greater than 1 character.', category='error')
    elif len(password) < 5:
        flash('Password must be at least 7 characters.', category='error')
    else:
        new_user = User(email=email, first_name=first_name, password=generate_password_hash(password, method='sha256'),
                        is_admin=is_admin, is_patient=is_patient, is_nurse=is_nurse)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created!', category='success')
        return new_user
    return None


def delete_user(id):
    data = User.query.get(id)
    db.session.delete(data)
    db.session.commit()
    flash("User Deleted Successfully")


def create_patient(patientID, username, first_name, mi_name, last_name, SSN, age, gender, race, occupation_class,
                   medical_history_description, phone_number, address):
    new_patient = Patient(patientID=patientID, username=username, first_name=first_name, mi_name=mi_name,
                          last_name=last_name,
                          SSN=SSN, age=age, gender=gender, race=race, occupation_class=occupation_class,
                          medical_history_description=medical_history_description, phone_number=phone_number,
                          address=address)
    db.session.add(new_patient)
    db.session.commit()
    flash('Patient created!', category='success')


@views.route('/my-account', methods=['GET', 'POST'])
def my_account():
    if current_user.is_patient:
        patient = Patient.query.filter_by(patientID=current_user.id).first()
        return render_template("my_account.html", user_patient=patient, user=current_user)
    elif current_user.is_nurse:
        nurse = Nurse.query.filter_by(employeeID=current_user.id).first()
        return render_template("my_account.html", user_nurse=nurse, user=current_user)
    else:
        return render_template("/errors/403.html", user=current_user)


@views.route('/update-account-info', methods=['GET', 'POST'])
def update_account_info():
    if request.method == 'POST':
        if current_user.is_nurse:
            data = Nurse.query.get(request.form.get('employeeID'))
            data.phoneNumber = request.form['phoneNumber']
            data.address = request.form['address']
        elif current_user.is_patient:
            data = Patient.query.get(request.form.get('patientID'))
            data.username = request.form['username']
            data.first_name = request.form['firstName']
            data.mi_name = request.form['miName']
            data.last_name = request.form['lastName']
            data.SSN = request.form['ssn']
            data.age = request.form['age']
            data.gender = request.form['gender']
            data.race = request.form['race']
            data.occupation_class = request.form['occupationClass']
            data.medical_history_description = request.form['medicalHistoryDescription']
            data.phone_number = request.form['phoneNumber']
            data.address = request.form['address']
        db.session.commit()
        flash("Information updated successfully.")
        return redirect(url_for('views.my_account'))


@views.route('/view-patients')
def view_patients():
    if current_user.is_anonymous or not current_user.is_authenticated or not current_user.is_admin:
        return render_template("/errors/403.html", user=current_user)
    patients = Patient.query.all()
    return render_template("/admin/view_patients.html", user=current_user, patients=patients)


@views.route('/view-all-nurse-schedules')
def view_all_nurse_schedules():
    if current_user.is_anonymous or not current_user.is_authenticated or not current_user.is_admin:
        return render_template("/errors/403.html", user=current_user)
    schedules = NurseSchedule.query.all()
    timeslots = convert_timeslots_to_dictionary(NurseScheduleTracker.query.all())
    return render_template("/admin/view_all_nurse_schedules.html", user=current_user, nurse_schedules=schedules, timeslots=timeslots)


@views.route('/view-vaccine-inventory')
def view_vaccine_inventory():
    if current_user.is_anonymous or not current_user.is_authenticated or not current_user.is_admin:
        return render_template("/errors/403.html", user=current_user)
    vaccines = Vaccine.query.all()
    return render_template("/admin/view_vaccine_inventory.html", user=current_user, vaccines=vaccines)


@views.route('/create-vaccine', methods=['POST'])
def create_vaccine():
    if not current_user.is_admin:
        return render_template("/errors/403.html", user=current_user)
    if request.method == 'POST':
        name = request.form['name']
        company_name = request.form['company_name']
        num_doses = request.form['num_doses']
        description = request.form['description']
        num_on_hold = request.form['num_on_hold']
        vaccine_name = Vaccine.query.filter_by(name=name).first()
        if vaccine_name:
            flash('Vaccine name already exists', category='error')
        else:
            new_vaccine = Vaccine(name=name, company_name=company_name, num_doses=num_doses, description=description,
                                  num_on_hold=num_on_hold)
            db.session.add(new_vaccine)
            db.session.commit()
            flash('Vaccine created!', category='success')
        return redirect(url_for('views.view_vaccine_inventory'))


@views.route('/update-vaccine', methods=['GET', 'POST'])
def update_vaccine():
    if request.method == 'POST':
        data = Vaccine.query.get(request.form.get('vaccineID'))
        data.name = request.form['name']
        data.company_name = request.form['company_name']
        data.num_doses = request.form['num_doses']
        data.description = request.form['description']
        data.num_on_hold = request.form['num_on_hold']
        db.session.commit()
        flash("Vaccine updated Sucessfully!")
        return redirect(url_for('views.view_vaccine_inventory'))


@views.route('/delete-vaccine/<id>/', methods=['GET', 'POST'])
def delete_vaccine(id):
    data = Vaccine.query.get(id)
    db.session.delete(data)
    db.session.commit()
    flash("Vaccine Deleted Successfully")
    return redirect(url_for('views.view_vaccine_inventory'))

@views.route('/create-appointment', methods=['POST'])
def create_appointment():
    if request.method == 'POST':
        appointment_time = request.form['appt_dateandtime']

    # convert date/time from calender to "%Y-%m-%d %H:%M:%S" format
    result = [letter.replace('T', ' ') for letter in appointment_time]
    result = ''.join(result)

    year = result[0:4]
    month = result[5:7]
    day = result[8:10]
    hour = result[11:13]

    appointment_time = datetime.datetime(int(year),int(month),int(day),int(hour))
    
    # check if appointment for THIS user already exists
    new_appt = Appointment.query.filter_by(appointment_time=appointment_time).first() 
    if new_appt:
        flash('Appointment already scheduled. Please select another time.', category='error')
    else:
        new_appt = Appointment(appointment_time=appointment_time, patientID=current_user.id)
        db.session.add(new_appt)
        db.session.commit()
        flash('Appointment created!', category='success')
    
    return redirect(url_for('views.schedule_appointment'))
    

@views.route('/schedule-appointment')
def schedule_appointment():
    if current_user.is_anonymous or not current_user.is_authenticated or not current_user.is_patient:
        return render_template("403.html", user=current_user)
    vaccines = Vaccine.query.all()
    schedules = NurseSchedule.query.all()

    # add appointments from database first
    events=[]
    appts = Appointment.query.all()
    for row in appts:
        dbEvent = {'available': 'DB APPOINTMENT', 'date' : row.appointment_time}
        events.append(dbEvent)

    # create all M-F, 8-5 blank appt slots
    weekdays = [5,6]
    start_time = 8
    end_time = 17

    def daterange(start, end):
        for n in range(int ((end-start).days)+1):
            yield start+timedelta(n)

    start = datetime.datetime(2021,4,20) # make this to 'todays' date
    end = datetime.datetime(2021,7,20) # make this automatically 1 year from 'today'

    # fill in rest of slots with empty appt slots
    for date in daterange(start, end):
        if date.weekday() not in weekdays:
            for t in range(start_time, end_time):
                if (date+timedelta(hours=t)).strftime("%Y-%m-%d %H:%M:%S") not in [d['date'].strftime("%Y-%m-%d %H:%M:%S") for d in events]:
                    events.append({'available' : "Schedule Appt", 'date' : date+timedelta(hours=t)})

    return render_template("schedule_appointment.html", user=current_user, vaccines=vaccines, nurse_schedules=schedules,
        events=events)
    return redirect(url_for('views.view_vaccine_inventory'))


@views.route('/view-nurse-schedule')
def view_nurse_schedule():
    if current_user.is_anonymous or not current_user.is_authenticated or not current_user.is_nurse:
        return render_template("/errors/403.html", user=current_user)
    schedule = NurseSchedule.query.filter_by(nurseID=current_user.id).all()
    return render_template("/nurse/view_nurse_schedule.html", user=current_user, schedule=schedule)


@views.route('/create-nurse-schedule', methods=['POST'])
def create_nurse_schedule():
    if not current_user.is_nurse:
        return render_template("/errors/403.html", user=current_user)
    if request.method == 'POST':
        start_time_str = request.form['start_time']
        end_time_str = request.form['end_time']
        if end_time_str == 'End Time' or start_time_str == 'Start Time':
            flash("Please enter start and end time.", category='error')
            return redirect(url_for('views.view_nurse_schedule'))
        start_time = str_to_datetime(start_time_str)
        end_time = str_to_datetime(end_time_str)
        nurse_schedule_lst = NurseSchedule.query.filter_by(nurseID=current_user.id)
        if check_schedules_for_conflict(nurse_schedule_lst, start_time, end_time):
            if add_schedule_count(start_time, end_time):
                new_schedule = NurseSchedule(nurseID=current_user.id, start_time=start_time, end_time=end_time)
                db.session.add(new_schedule)
                db.session.commit()
                flash('Schedule created Sucessfully!', category='success')
    return redirect(url_for('views.view_nurse_schedule'))


@views.route('/update-nurse-schedule', methods=['GET', 'POST'])
def update_nurse_schedule():
    if request.method == 'POST':
        data = NurseSchedule.query.get(request.form.get('scheduleID'))
        start_time_str = request.form['start_time']
        end_time_str = request.form['end_time']
        start_time = str_to_datetime_v2(start_time_str)
        end_time = str_to_datetime_v2(end_time_str)
        nurse_schedule_lst = NurseSchedule.query.filter_by(nurseID=current_user.id)
        if check_schedules_for_conflict(nurse_schedule_lst, start_time, end_time, data.scheduleID, True):
            data.start_time = start_time
            data.end_time = end_time
            db.session.commit()
            flash("Schedule updated Sucessfully!")
    return redirect(url_for('views.view_nurse_schedule'))


@views.route('/delete-nurse-schedule/<id>/', methods=['GET', 'POST'])
def delete_nurse_schedule(id):
    schedule = NurseSchedule.query.get(id)
    remove_schedule_count(schedule.start_time, schedule.end_time)
    db.session.delete(schedule)
    db.session.commit()
    flash("Schedule Deleted Successfully")
    return redirect(url_for('views.view_nurse_schedule'))
