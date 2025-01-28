from datetime import datetime, date
from datetime import timedelta
from django.utils import timezone


LESSON_SELECT_CHOICE =(
    ('special_lesson','I Need a special lesson'),
    ('hire_car','I want to hire a car'),
)

HIRE_CAR_STATUS= [ 
    ('Pending', 'Pending'),
    ('Rejected', 'Rejected'), 
    ('Paid', 'Paid')
    ]

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
        
        current_time += timedelta(minutes=schedule.lesson_gap + (schedule.lesson_duration * 60))

    return available_times



def calculate_end_time(start_time, operation_hour, lesson_duration, lesson_gap, 
                       launch_break_start, launch_break_end, extra_space_start, extra_space_end):
    start_datetime = datetime.combine(datetime.today(), start_time)
    end_time = start_datetime + timedelta(hours=operation_hour)

    current_time = start_datetime
    lesson_schedule = []
    break_schedule = []
    extra_space_schedule = []

    break_added = False
    extra_space_added = False

    def add_break_if_needed():
        nonlocal current_time, break_added
        if not break_added and launch_break_start and current_time.time() <= launch_break_start < (current_time + timedelta(hours=lesson_duration)).time():
            # Add free time before the break
            if current_time.time() < launch_break_start:
                free_time_start = current_time.time()
                free_time_end = launch_break_start
                break_schedule.append((free_time_start, free_time_end))
            
            break_schedule.append((launch_break_start, launch_break_end))
            current_time = datetime.combine(datetime.today(), launch_break_end)  
            break_added = True

    def add_extra_space_if_needed():
        nonlocal current_time, extra_space_added
        if not extra_space_added and extra_space_start and current_time.time() <= extra_space_start < (current_time + timedelta(hours=lesson_duration)).time():
            # Add free time before the extra space
            if current_time.time() < extra_space_start:
                free_time_start = current_time.time()
                free_time_end = extra_space_start
                extra_space_schedule.append((free_time_start, free_time_end))
            
            # Add the extra space
            extra_space_schedule.append((extra_space_start, extra_space_end))
            current_time = datetime.combine(datetime.today(), extra_space_end)  
            extra_space_added = True

    while current_time < end_time:
        add_break_if_needed()
        add_extra_space_if_needed()

        lesson_end = current_time + timedelta(hours=lesson_duration)

        if lesson_end > end_time:
            lesson_end = end_time

        lesson_schedule.append((current_time.time(), lesson_end.time()))

        current_time = lesson_end

        if current_time < end_time:
            gap_end = current_time + timedelta(minutes=lesson_gap)
            if gap_end > end_time:
                gap_end = end_time
            if not break_added and launch_break_start and gap_end.time() >= launch_break_start:
                break_schedule.append((current_time.time(), gap_end.time()))
            elif not extra_space_added and extra_space_start and gap_end.time() >= extra_space_start:
                extra_space_schedule.append((current_time.time(), gap_end.time()))
            else:
                break_schedule.append((current_time.time(), gap_end.time()))
            current_time = gap_end

    return {
        "lessons": lesson_schedule,
        "breaks": break_schedule,
        "extra_spaces": extra_space_schedule,
        "end_time": lesson_schedule[-1][1] if lesson_schedule else end_time.time()
    }



def validate_even_or_odd(operation_hour: int, lesson_duration: int):
    if operation_hour % 2 != lesson_duration % 2:
        raise ValueError("Operation hour and lesson duration must both be even or both odd.")
    return True