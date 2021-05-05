from flask_login import current_user

from .models import Nurse, User, Patient, NurseScheduleTracker, NurseSchedule, Vaccine, AllNursesScheduleTracker, \
    Appointment, VaccinationRecord
from flask import flash
from . import db
from datetime import datetime, timedelta
from sqlalchemy import func


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


def add_count_to_schedule_tracker(start_time, end_time, nurseID):
    time_slots = []
    while start_time <= end_time:
        start_datehour_str = start_time.strftime("%Y-%m-%d %H:00")
        time_slot = AllNursesScheduleTracker.query.filter_by(timestamp=start_datehour_str).first()
        if time_slot:
            if time_slot.count == 12:
                flash(
                    "The schedule you entered has at least one timeslot with 12 nurses scheduled. Please choose a "
                    "different start and end time.",
                    category='error')
                return 0
            time_slots.append(time_slot)
        else:
            new_time_slot = AllNursesScheduleTracker(timestamp=start_datehour_str, count=0)
            db.session.add(new_time_slot)
            time_slots.append(new_time_slot)
        individual_time_slot = NurseScheduleTracker(nurseID=nurseID, timestamp=start_datehour_str)
        db.session.add(individual_time_slot)
        start_time += timedelta(hours=1)
    for time_slot in time_slots:
        time_slot.count += 1
    db.session.commit()
    return 1


def remove_schedule_count(start_time, end_time):
    """
    Delete all timeslots between given start and end time
    Update All Nurses Schedule Tracker table
    """
    while start_time <= end_time:
        start_datehour_str = start_time.strftime("%Y-%m-%d %H:00")
        time_slot = AllNursesScheduleTracker.query.filter_by(timestamp=start_datehour_str).first()
        if time_slot:
            time_slot.count -= 1
            if time_slot.count <= 0:
                db.session.delete(time_slot)
        db.session.commit()
        start_time += timedelta(hours=1)


def remove_inactive_schedules():
    """
    Add hours for each date and a count of nurses at the timeslot to dictionary
    """
    schedules = AllNursesScheduleTracker.query.all()
    for schedule in schedules:
        if datetime.strptime(schedule.timestamp, "%Y-%m-%d %H:00") < datetime.now() - timedelta(days=1):
            print("Deleted schedule time-slot" + schedule.timestamp)
            db.session.delete(schedule)
    db.session.commit()


def convert_timeslots_to_dictionary(timeslots):
    """
    Return dictionary
               (str)       (str)        (str)            (int)
             { date : {'start time': ['end time', Count of Nurses Scheduled] }

    Add hours for each date and a count of nurses at the timeslot to dictionary
    """
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
    """
    Return dictionary with all scheduled appointments for patient

    Query all scheduled appointments for patient using given id
    and store into events dictionary marked as 'Your Appointment'
    """
    appts = Appointment.query.filter_by(patientID=id)
    events = {}
    for appt in appts:
        event = {'available': 'Your Appointment', 'color': '#ce4409'}
        date_str = datetime.strptime(appt.appointment_time, "%Y-%m-%d %H:00")
        events[date_str] = event
    return events


def daterange(start, end):
    for n in range(int((end - start).days) + 1):
        yield start + timedelta(n)


def delete_user(id):
    """
    Delete user using the id given
    Query the row in the User table and delete it
    """
    data = User.query.get(id)
    db.session.delete(data)
    db.session.commit()
    flash("User Deleted Successfully")


def create_patient(patientID, username, first_name, mi_name, last_name, SSN, age, sex, race, occupation_class,
                   medical_history_description, phone_number, address):
    """
    Create patient using the fields given
    Make a new Patient model and save in Patients table
    """
    new_patient = Patient(patientID=patientID, username=username, first_name=first_name, mi_name=mi_name,
                          last_name=last_name,
                          SSN=SSN, age=age, sex=sex, race=race, occupation_class=occupation_class,
                          medical_history_description=medical_history_description, phone_number=phone_number,
                          address=address)
    db.session.add(new_patient)
    db.session.commit()
    flash('Patient created!', category='success')


def get_nurse_id_by_availability(appt_time):
    """
    Return nurseID

    Query Nurse Schedule Tracker table and filter by date. Iterate through timeslots
    found and return nurseID of nurse that is available at the given time otherwise return -1
    """
    if isinstance(appt_time, datetime):
        date_str = appt_time.strftime("%Y-%m-%d %H:00")
    else:
        date_str = appt_time
    timeslot_nurseID = db.session.query(
        NurseScheduleTracker.timestamp.label('Timestamp'), NurseScheduleTracker.nurseID.label('NurseID')) \
        .where(NurseScheduleTracker.timestamp == date_str).all()
    for timeslot_id in timeslot_nurseID:
        id = timeslot_id.NurseID
        timeslot = timeslot_id.Timestamp
        nurse_appointment_count = db.session.query(
            func.count(Appointment.appointmentID).label('AppointmentCount')) \
            .where((Appointment.nurseID == id) & (Appointment.appointment_time == timeslot)).first()
        num_appointments = nurse_appointment_count[0]
        if num_appointments < 10:
            return id
    return -1


def get_nurse_appointment_counts_by_timeslot(cur_date):
    """
    Return query result

    Query Nurse Schedule Tracker table of all timeslots and nurseIDs
    of nurses working at the timeslot and filter by date
    """
    date_str = cur_date.strftime("%Y-%m-%d %H:00")
    timeslot_nurseID = db.session.query(
        NurseScheduleTracker.timestamp.label('Timestamp'), NurseScheduleTracker.nurseID.label('NurseID')) \
        .where(NurseScheduleTracker.timestamp == date_str).all()
    return timeslot_nurseID


def fetch_calendar_events_based_on_availability(events, start_date, end_date, start_time, end_time):
    """
    Return a dictionary
                (str)        (str)             (str)            (str)   (str)
             {timeslot : {'available': 'Schedule Appointment', 'color':'green'} }

    For every nurse scheduled at each timeslot, get appointment count that is working at the timeslot.
    When we find at least one nurse that is available at a given timeslot, mark event as available and look
    for availability for next timeslot. If at the end if we've found no availability, mark event as unavailable.
    Dictionary returned is used to populate all available/unavailable events on the calendar.
    """
    for _date in daterange(start_date, end_date):
        for _time in range(start_time, end_time):
            cur_date = _date + timedelta(hours=_time)
            timeslot_nurseID = get_nurse_appointment_counts_by_timeslot(cur_date)
            for timeslot_id in timeslot_nurseID:
                id = timeslot_id.NurseID
                timeslot = timeslot_id.Timestamp
                nurse_appointment_count = db.session.query(
                    func.count(Appointment.appointmentID).label('AppointmentCount')) \
                    .where((Appointment.nurseID == id) & (Appointment.appointment_time == timeslot)).first()
                num_appointments = nurse_appointment_count[0]
                if num_appointments < 10:
                    if (cur_date not in events.keys()) \
                            or cur_date in events.keys() and events[cur_date]['color'] != '#ce4409':
                        event = {'available': "Schedule Appointment", 'color': "green"}
                        events[cur_date] = event
                        timeslot_nurseID = list(filter(lambda x: x[0] != timeslot, timeslot_nurseID))
                        break
                elif (cur_date not in events.keys()) \
                        or (cur_date in events.keys() and events[cur_date]['color'] != '#ce4409'):
                    if num_appointments >= 10:
                        event = {'available': "Not available", 'color': "red"}
                        events[cur_date] = event
    return events


def get_vaccine_count_by_name(vaccine_type):
    """
    Return int

    Query vaccine count for given vaccine name and filter by vaccine type
    return its count
    """
    data = Vaccine.query.filter_by(name=vaccine_type).first()
    return data.num_doses if data else 0


def decrease_vaccine_count(vaccine_type):
    """
    Decrease vaccine count of given vaccine type
    Query and filter by vaccine type and decrement count for doses and increment count on hold
    """
    data = Vaccine.query.filter_by(name=vaccine_type).first()
    data.num_doses -= 1
    data.num_on_hold += 1
    db.session.commit()


def increase_vaccine_count(vaccine_type):
    """
    Increase vaccine count of given vaccine type
    Query and filter by vaccine type and increment count for doses and decrease count on hold
    """
    data = Vaccine.query.filter_by(name=vaccine_type).first()
    data.num_doses += 1
    data.num_on_hold -= 1
    db.session.commit()


def can_schedule_appointment(patientID):
    """
    Return list [boolean, str] of two elements:
        1. Whether patient can schedule an appointment
        2. Name of vaccine type

    [True, vaccineType] denotes that the patient has had one dose of either Pfizer or Moderna and
    can schedule an appointment for their second vaccination shot.
    [False, ''] or [False, 'johnson'] means that the patient is fully vaccinated.
    """
    vaccinations = VaccinationRecord.query.filter_by(patientID=patientID).all()
    vaccination_count = len(vaccinations)
    if vaccination_count == 0:
        return [True, '']
    elif vaccination_count == 1:
        vaccineID = vaccinations[0].vaccineID
        vaccine = Vaccine.query.filter_by(vaccineID=vaccineID).first()
        vaccineName = vaccine.name
        if vaccineName == 'pfizer' or vaccineName == 'moderna':
            return [True, vaccineName]
        else:
            return [False, vaccineName]
    else:
        return [False, '']
