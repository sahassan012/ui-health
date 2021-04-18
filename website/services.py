from .models import Nurse_Schedule
from flask import flash
from datetime import datetime

def check_schedules_for_conflict(schedules, start_time, end_time, schedule_id=None, updating=False):
    if end_time <= start_time:
        flash("The given start time was after the end time.", category='error')
        return 0
    for schedule in schedules:
        if schedule.start_time == start_time and schedule.end_time == end_time:
            flash("The given start and end time already exist.", category='error')
            return 0
        elif (start_time >= schedule.start_time and end_time <= schedule.end_time):
            if updating and schedule_id == schedule.scheduleID:
                continue
            flash("The given schedule's start and end time conflicts with an existing schedule.", category='error')
            return 0
        elif (start_time >= schedule.start_time and start_time < schedule.end_time):
            if updating and schedule_id == schedule.scheduleID:
                continue
            flash("The given schedule's start time conflicts with an existing schedule.", category='error')
            return 0
        elif (end_time <= schedule.end_time and end_time > schedule.start_time):
            if updating and schedule_id == schedule.scheduleID:
                continue
            flash("The given schedule's end time conflicts with an existing schedule.", category='error')
            return 0
        elif (start_time > schedule.start_time and start_time < schedule.end_time) or (end_time > schedule.start_time and end_time < schedule.end_time):
            if updating and schedule_id == schedule.scheduleID:
                continue
            flash("The given start and end time conflicts with an existing schedule.", category='error')
            return 0
        elif (start_time < schedule.start_time and end_time > schedule.end_time):
            if updating and schedule_id == schedule.scheduleID:
                continue
            flash("The given start and end time conflicts with an existing schedule.", category='error')
            return 0
    return 1

def str_to_datetime(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d %I:%M:%S %p")

def str_to_datetime_v2(date_str):
    if (date_str[-1] == 'm'):
        return datetime.strptime(date_str, "%Y-%m-%d %I:%M %p")
    else:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")