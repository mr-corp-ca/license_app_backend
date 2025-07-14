
from celery import shared_task
from timing_slot_app.models import LearnerBookingSchedule
from django.utils import timezone
from datetime import date
from django.db.models import Q
from user_management_app.constants import get_masked_phone_number
from user_management_app.models import SchoolProfile, User, UserNotification, UserNotificationsType
from user_management_app.threads import send_push_notification
from datetime import timedelta

@shared_task
def send_course_progress_notifications():
    # Get all users who have bookings (adjust query as needed)
    users = User.objects.filter(
        learner_booking_schedules__isnull=False
    ).distinct()

    for user in users:
        obj, created = UserNotificationsType.objects.get_or_create(user=user)
        if obj.is_course_progress:
            learner_bookings = LearnerBookingSchedule.objects.filter(user=user)
            total_bookings = learner_bookings.count()

            if total_bookings == 0:
                continue  # Skip if no bookings

            today = timezone.now().date()
            completed_bookings = learner_bookings.filter(date__lt=today).count()
            percentage_complete = (completed_bookings / total_bookings) * 100

            # Determine progress and send notification
            title = ""
            message = ""
            progress_made = False

            if percentage_complete >= 100 and user.course_progress != 'done':
                title = "🎉 Lesson Complete! 100% Finished!"  
                message = "Congratulations! 🎉 You've successfully completed the lesson. Ready for the next challenge?"  
                user.course_progress = 'done'
                progress_made = True

            elif percentage_complete >= 75 and user.course_progress != '100':
                title = "🚀 Almost Done! 75% Complete!"  
                message = "You're crushing it! Just a little more to finish this lesson. 🔥"  
                user.course_progress = '100'
                progress_made = True

            elif percentage_complete >= 50 and user.course_progress != '75':
                title = "🎯 Halfway There! 50% Complete!"  
                message = "Great job! You've made it halfway through the lesson. Don't stop now! 💪"  
                user.course_progress = '75'
                progress_made = True

            elif percentage_complete >= 25 and user.course_progress != '50':
                title = "📚 Lesson Progress: 25% Complete!"  
                message = "Keep going! You're just getting started. Tap to continue learning! ✨"  
                user.course_progress = '50'
                progress_made = True

            if progress_made:
                user.save()
                noti_type = 'general'
                send_push_notification(user, title, message, noti_type)
                UserNotification.objects.create(
                    user=user,
                    title=title,
                    text=message,
                    noti_type=noti_type
                )
            obj.is_course_progress = False
            obj.save()


@shared_task
def check_incomplete_profiles():
    # Get users with incomplete profiles
    incomplete_users = User.objects.filter(
        Q(full_name__isnull=True) |
        Q(phone_number__isnull=True) |
        Q(email__isnull=True) | 
        Q(province__isnull=True) | 
        Q(city__isnull=True)
    )
    
    # Send notifications for incomplete users
    for user in incomplete_users:
        obj, created = UserNotificationsType.objects.get_or_create(user=user)
        if obj.is_profile_complete:
            title="📋 Profile Incomplete",
            message="Please complete your profile to access all features!",
            noti_type = 'general'

            send_push_notification(
                user=user,
                title=title,
                message=message,
                noti_type=noti_type
            )
            user_status = 'pending'
            send_push_notification(user, title, message, noti_type)
            UserNotification.objects.create(
                user=user,
                title=title,
                text=message,
                status=user_status,
                noti_type=noti_type
            )
            obj.is_profile_complete = False
            obj.save()
        
        # Get list of incomplete user IDs to exclude
        incomplete_user_ids = list(incomplete_users.values_list('id', flat=True))
        
        # Check SchoolProfiles, excluding users already marked incomplete
        incomplete_schools = SchoolProfile.objects.filter(
            Q(institute_name__isnull=True) |
            Q(instructor_name__isnull=True) |
            Q(registration_file__isnull=True)
        ).exclude(user_id__in=incomplete_user_ids) 

        # Send notifications for incomplete school profiles
    for school in incomplete_schools:
        school_obj, created = UserNotificationsType.objects.get_or_create(user=school.user)
        if school_obj.is_profile_complete:
            title="🏫 School Profile Incomplete",
            message="Your school profile is missing required details. Update it now!",
            noti_type = 'general'

            send_push_notification(
                user=school.user,
                title=title,
                message=message,
                noti_type=noti_type
            )
            UserNotification.objects.create(
                user=school.user,
                title=title,
                text=message,
                status=user_status,
                noti_type=noti_type
            )
            school_obj.is_profile_complete = False
            school_obj.save()


@shared_task
def send_lesson_reminder_day_before():
    # Calculate tomorrow's date
    tomorrow = timezone.now().date() + timedelta(days=1)
    
    # Get all lessons scheduled for tomorrow
    tomorrow_lessons = LearnerBookingSchedule.objects.filter(date=tomorrow)
    
    for lesson in tomorrow_lessons:
        # Send notification to learner (user)
        leaner_obj, created = UserNotificationsType.objects.get_or_create(user=lesson.user)
        school_obj, created = UserNotificationsType.objects.get_or_create(user=lesson.vehicle.user)
        if leaner_obj.is_lesson_reminder1:
            title="⏰ Lesson Reminder",
            message=f"You have a lesson scheduled tomorrow at {lesson.slot}",
            noti_type = 'general'

            send_push_notification(
                user=lesson.user,
                title=title,
                message=message,
                noti_type=noti_type
            )
            UserNotification.objects.create(
                user=lesson.user,
                title=title,
                text=message,
                noti_type=noti_type
            )
            leaner_obj.is_lesson_reminder1 = False
            leaner_obj.save()
        if school_obj.is_lesson_reminder1:
            # Send notification to instructor (vehicle's user)
            title="⏰ Lesson Reminder",
            message=f"You have a lesson scheduled tomorrow at {lesson.slot} with {get_masked_phone_number(lesson.user)}",
            send_push_notification(
                user=lesson.vehicle.user,
                title=title,
                message=message,
                noti_type=noti_type
            )
            UserNotification.objects.create(
                user=lesson.vehicle.user,
                title=title,
                text=message,
                noti_type=noti_type
            )
            school_obj.is_lesson_reminder1 = False
            school_obj.save()

@shared_task
def send_lesson_reminder_5_min_before():
    # Calculate time 5 minutes from now
    reminder_time = timezone.now() + timedelta(minutes=5)
    
    # Get all lessons that start in 5 minutes
    upcoming_lessons = LearnerBookingSchedule.objects.filter(
        date=reminder_time.date(),
        slot__hour=reminder_time.hour,
        slot__minute=reminder_time.minute
    )
    
    for lesson in upcoming_lessons:
        # Send notification to learner (user)
        leaner_obj, created = UserNotificationsType.objects.get_or_create(user=lesson.user)
        school_obj, created = UserNotificationsType.objects.get_or_create(user=lesson.vehicle.user)
        if leaner_obj.is_lesson_reminder2:
        
            title="⏰ Lesson Starting Soon",
            message=f"Your lesson starts in 5 minutes at {lesson.location}",
            noti_type = 'general'

            send_push_notification(
                user=lesson.user,
                title=title,
                message=message,
                noti_type=noti_type
            )

            UserNotification.objects.create(
                user=lesson.user,
                title=title,
                text=message,
                noti_type=noti_type
            )
            leaner_obj.is_lesson_reminder2 = False
            leaner_obj.save()
        if school_obj.is_lesson_reminder2:
            
            # Send notification to instructor (vehicle's user)
            title="⏰ Lesson Starting Soon",
            message=f"Your lesson with {get_masked_phone_number(lesson.user)} starts in 5 minutes at {lesson.location}",
            send_push_notification(
                user=lesson.vehicle.user,
                title=title,
                message=message,
                noti_type=noti_type
            )
            UserNotification.objects.create(
                user=lesson.vehicle.user,
                title=title,
                text=message,
                noti_type=noti_type
            )
            school_obj.is_lesson_reminder2 = False
            school_obj.save()

# Ad Campaign
@shared_task
def notification_checks():

    UserNotificationsType.objects.all().update(
                    is_lesson_reminder1=True, 
                    is_lesson_reminder2=True, 
                    is_course_progress=True, 
                    is_profile_complete=True, 
                )