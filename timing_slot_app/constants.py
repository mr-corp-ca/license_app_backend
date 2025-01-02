from datetime import datetime, date
from datetime import timedelta
from django.utils import timezone


LESSON_SELECT_CHOICE =(
    ('special_lesson','I Need a special lesson'),
    ('hire_car','I want to hire a car'),
)

def get_day_name(date_input):
    """
    Returns the day name for a given date input.

    Args:
    date_input (str or datetime.date): Date in string format 'YYYY-MM-DD' or a datetime.date object.

    Returns:
    str: Day name (e.g., Monday, Tuesday, etc.).
    """
    try:
        if isinstance(date_input, str):
            date_object = datetime.strptime(date_input, "%Y-%m-%d").date()
        elif isinstance(date_input, date):
            date_object = date_input
        else:
            raise ValueError("Invalid input type. Provide a date string or datetime.date.")

        return date_object.strftime("%A")
    except Exception as e:
        return ""


def get_schedule_times(schedule):
    from timing_slot_app.models import LearnerBookingSchedule

    start_time = timezone.datetime.combine(schedule.date, schedule.start_time)
    end_time = timezone.datetime.combine(schedule.date, schedule.end_time)

    # If break times are set, convert them to datetime objects
    if schedule.launch_break_start and schedule.launch_break_end:
        launch_break_start = timezone.datetime.combine(schedule.date, schedule.launch_break_start)
        launch_break_end = timezone.datetime.combine(schedule.date, schedule.launch_break_end)
    else:
        launch_break_start = launch_break_end = None

    learner_bookings = LearnerBookingSchedule.objects.filter(date=schedule.date)

    available_times = []

    current_time = start_time
    while current_time <= end_time:
        conflict = learner_bookings.filter(slot__gte=current_time.time(), slot__lt=(current_time + timedelta(minutes=15)).time()).exists()

        if not conflict:
            if launch_break_start and launch_break_end:
                if not (launch_break_start <= current_time <= launch_break_end):
                    available_times.append(current_time.time())
            else:
                available_times.append(current_time.time())
        
        current_time += timedelta(minutes=60)

    return available_times

