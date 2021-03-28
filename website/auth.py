from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy import or_
from .models import User, Nurse, Patient
from .views import create_user, create_patient
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        usertype = request.form.get('usertype')
        username = request.form.get('username')
        password = request.form.get('password')

        if usertype == 'nurse':
            nurse = Nurse.query.filter(or_(Nurse.username == username, Nurse.email == username)).first()
            if nurse:
                user = User.query.filter_by(id=nurse.employeeID).first()
                if check_password_hash(user.password, password):
                    if user.is_nurse:
                        flash('Logged in successfully as Nurse!', category='success')
                        login_user(user, remember=True)
                        return redirect(url_for('views.home'))
                    else:
                        flash('Choose correct account type.', category='error')
                else:
                    flash('Incorrect password, try again.', category='error')
        elif usertype == 'admin':
            user = User.query.filter_by(email=username).first()
            if user:
                if check_password_hash(user.password, password):
                    if user.is_admin:
                        flash('Logged in successfully as Admin!', category='success')
                        login_user(user, remember=True)
                        return redirect(url_for('views.home'))
                    else:
                        flash('You don\'t have admin access. Choose correct account type.', category='error')
                else:
                    flash('Incorrect password, try again.', category='error')
            else:
                flash('Username/Email does not exist.', category='error')
        if usertype == 'patient':
            user = User.query.filter_by(email=username).first()
            patient = Patient.query.filter_by(username=username).first()
            if user:
                if check_password_hash(user.password, password):
                    if user.is_patient:
                        flash('Logged in successfully as Patient!', category='success')
                        login_user(user, remember=True)
                        return redirect(url_for('views.home'))
                    else:
                        flash('Choose correct account type.', category='error')
                else:
                    flash('Incorrect password, try again.', category='error')
            elif patient:
                user = User.query.filter_by(id=patient.patientID).first()
                if check_password_hash(user.password, password):
                    if user.is_patient:
                        flash('Logged in successfully as Patient!', category='success')
                        login_user(user, remember=True)
                        return redirect(url_for('views.home'))
                    else:
                        flash('Choose correct account type.', category='error')
                else:
                    flash('Incorrect password, try again.', category='error')
            else:
                flash('Username/Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', category='success')
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        first_name = request.form.get('firstName')
        mi_name = request.form.get('miName')
        last_name = request.form.get('lastName')
        SSN = request.form.get('ssn')
        age = request.form.get('age')
        gender = request.form.get('gender')
        race = request.form.get('race')
        occupation_class = request.form.get('occupationClass')
        medical_history_description = request.form.get('medicalHistoryDescription')
        phone_number = request.form.get('phoneNumber')
        address = request.form.get('address')
        
        user_email_check = User.query.filter_by(email=email).first()
        user_SSN_check = Patient.query.filter_by(SSN=SSN).first()
        if user_email_check:
            flash('Email already exists.', category='error')
        elif user_SSN_check:
            flash('SSN already exists.', category='error')
        elif email == 'admin':
            new_user = User(email=email, first_name='Admin', password=generate_password_hash('password', method='sha256'), is_admin=True)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Admin account created.', category='success')
            return redirect(url_for('views.home'))
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = create_user(email, first_name, password1, False, True, False)
            create_patient(new_user.id, username, first_name, mi_name, last_name, SSN, age, gender, race, occupation_class, medical_history_description, phone_number, address)
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))
    return render_template("sign_up.html", user=current_user)