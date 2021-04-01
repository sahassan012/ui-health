from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from .models import Nurse, User, Patient
from . import db
import json

views = Blueprint('views', __name__)

DB_NAME = "database.db"


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # If admin, show admin page
    if (current_user.is_admin):
        return render_template("admin.html", user=current_user)
    return render_template("home.html", user=current_user)

@views.route('/register-nurse')
def register_nurse():
    if current_user.is_anonymous or not current_user.is_authenticated or not current_user.is_admin:
        return render_template("403.html", user=current_user)
    nurses = Nurse.query.all()
    return render_template("register_nurse.html", user=current_user, nurses = nurses)

@views.route('/create-nurse', methods = ['POST'])
def create_nurse():
    if not current_user.is_admin:
        return render_template("403.html", user=current_user)
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
            if user == None:
                flash('Something went wrong!', category='error')
            else:
                new_nurse = Nurse(employeeID = user.id, email=email, username=username, gender=gender, name=name, age=age, phoneNumber=phoneNumber, address=address)
                db.session.add(new_nurse)
                db.session.commit()
                flash('Nurse created!', category='success')
        return redirect(url_for('views.register_nurse'))


@views.route('/update-nurse', methods = ['GET', 'POST'])
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

@views.route('/delete-nurse/<id>/', methods = ['GET', 'POST'])
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
        new_user = User(email=email, first_name=first_name, password=generate_password_hash(password, method='sha256'), is_admin=is_admin, is_patient=is_patient, is_nurse=is_nurse)
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

def create_patient(patientID, username, first_name, mi_name, last_name, SSN, age, gender, race, occupation_class, medical_history_description, phone_number, address):
    new_patient = Patient(patientID=patientID, username=username, first_name=first_name, mi_name=mi_name, last_name=last_name, 
                          SSN=SSN, age=age, gender=gender, race=race, occupation_class=occupation_class, 
                          medical_history_description=medical_history_description, phone_number=phone_number, address=address)
    db.session.add(new_patient)
    db.session.commit()
    flash('Patient created!', category='success')

@views.route('/my-account', methods = ['GET', 'POST'])
def my_account():
    if current_user.is_patient:
        patient = Patient.query.filter_by(patientID = current_user.id).first()
        return render_template("my_account.html", user_patient=patient, user=current_user)
    elif current_user.is_nurse:
        nurse = Nurse.query.filter_by(employeeID = current_user.id).first()
        return render_template("my_account.html", user_nurse=nurse, user=current_user)
    else:
        return render_template("403.html", user=current_user)

@views.route('/update-account-info', methods = ['GET', 'POST'])
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