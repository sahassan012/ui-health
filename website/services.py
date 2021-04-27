from flask_login import current_user

from .models import Nurse, User, Patient, NurseSchedule, Vaccine, NurseScheduleTracker, Appointment
from flask import flash
from . import db
from datetime import datetime, timedelta


def check_schedules_for_conflict(schedules, start_time, end_time, schedule_id=None, updating=False):
    if end_time <= start_time:
        flash("The given start time was after the end time.", category='error')
        return 0
    elif start_time < datetime.today() or end_time < datetime.today():
        flash("Start and end date must be in the future.", category='error')
        return 0
    elif start_time > datetime.today() + timedelta(days=7) or end_time > datetime.today() + timedelta(days=7):
        flash("Start and end date must be within 7 days from today.", category='error')
        return 0

    for schedule in schedules:
        if schedule.start_time == start_time and schedule.end_time == end_time:
            flash("The given start and end time already exist.", category='error')
            return 0
        elif start_time >= schedule.start_time and end_time <= schedule.end_time:
            if updating and schedule_id == schedule.scheduleID:
                continue
            flash("The given schedule's start and end time conflicts with an existing schedule.", category='error')
            return 0
        elif schedule.start_time <= start_time < schedule.end_time:
            if updating and schedule_id == schedule.scheduleID:
                continue
            flash("The given schedule's start time conflicts with an existing schedule.", category='error')
            return 0
        elif schedule.end_time >= end_time > schedule.start_time:
            if updating and schedule_id == schedule.scheduleID:
                continue
            flash("The given schedule's end time conflicts with an existing schedule.", category='error')
            return 0
        elif (schedule.start_time < start_time < schedule.end_time) or (
                schedule.start_time < end_time < schedule.end_time):
            if updating and schedule_id == schedule.scheduleID:
                continue
            flash("The given start and end time conflicts with an existing schedule.", category='error')
            return 0
        elif start_time < schedule.start_time and end_time > schedule.end_time:
            if updating and schedule_id == schedule.scheduleID:
                continue
            flash("The given start and end time conflicts with an existing schedule.", category='error')
            return 0
    return 1


def str_to_datetime(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d %I:%M:%S %p")


def str_to_datetime_v2(date_str):
    if date_str[-1] == 'm':
        return datetime.strptime(date_str, "%Y-%m-%d %I:%M %p")
    else:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")


def add_schedule_count(start_time, end_time):
    time_slots = []
    while start_time <= end_time:
        start_datehour_str = start_time.strftime("%Y-%m-%d %H:00")
        time_slot = NurseScheduleTracker.query.filter_by(timestamp=start_datehour_str).first()
        if time_slot:
            if time_slot.count == 12:
                flash(
                    "The schedule you entered has atleast one timeslot with 12 nurses scheduled. Please choose a "
                    "different start and end time.",
                    category='error')
                return 0
            time_slots.append(time_slot)
        else:
            new_time_slot = NurseScheduleTracker(timestamp=start_datehour_str, count=0)
            db.session.add(new_time_slot)
            time_slots.append(new_time_slot)
        start_time += timedelta(hours=1)
    for time_slot in time_slots:
        time_slot.count += 1
    db.session.commit()
    return 1


def remove_schedule_count(start_time, end_time):
    while start_time <= end_time:
        start_datehour_str = start_time.strftime("%Y-%m-%d %H:00")
        time_slot = NurseScheduleTracker.query.filter_by(timestamp=start_datehour_str).first()
        if time_slot:
            time_slot.count -= 1
            if time_slot.count <= 0:
                db.session.delete(time_slot)
        db.session.commit()
        start_time += timedelta(hours=1)


def remove_inactive_schedules():
    schedules = NurseScheduleTracker.query.all()
    for schedule in schedules:
        if datetime.strptime(schedule.timestamp, "%Y-%m-%d %H:00") < datetime.now() - timedelta(days=1):
            print("Deleted schedule time-slot" + schedule.timestamp)
            db.session.delete(schedule)
    db.session.commit()


def convert_timeslots_to_dictionary(timeslots):
    timeslot_dictionary = {}
    for timeslot in timeslots:
        timeslot_start_str = datetime.strptime(timeslot.timestamp, "%Y-%m-%d %H:00")
        timeslot_end_str = datetime.strptime(timeslot.timestamp, "%Y-%m-%d %H:00")
        timeslot_end_str += timedelta(hours=1)
        timeslot_day_str = timeslot_start_str.strftime("%Y-%m-%d")
        timeslot_start_hour_str = timeslot_start_str.strftime("%H:00")
        timeslot_end_hour_str = timeslot_end_str.strftime("%H:00")
        new_slot = {timeslot_start_hour_str: [timeslot_end_hour_str, timeslot.count]}
        if timeslot_day_str in timeslot_dictionary:
            timeslot_dictionary[timeslot_day_str].update(new_slot)
        else:
            timeslot_dictionary[timeslot_day_str] = new_slot
    timeslot_dictionary = dict(sorted(timeslot_dictionary.items()))
    return timeslot_dictionary


def get_scheduled_appointments(id):
    appts = Appointment.query.filter_by(patientID=id)
    events = {}
    for appt in appts:
        event = {'available': 'Your Appointment', 'color': '#ce4409'}
        events[appt.appointment_time] = event
    return events


def daterange(start, end):
    for n in range(int((end - start).days) + 1):
        yield start + timedelta(n)


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