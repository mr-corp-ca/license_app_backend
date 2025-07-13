from course_management_app.models import Course
from course_management_app.serializers import VehicleSerializer
from rest_framework import serializers
from timing_slot_app.constants import get_day_name
from user_management_app.models import SchoolProfile, User
from user_management_app.serializers import DefaultUserSerializer, SchoolProfileSerializer
from utils_app.models import Location
from utils_app.serializers import LocationSerializer
from .models import LearnerBookingSchedule, MonthlySchedule, SpecialLesson
from datetime import date
from django.conf import settings


class MonthlyScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlySchedule
        fields = ['date', 'start_time', 'end_time', 'launch_break_start', 'launch_break_end', 'extra_space_start', 'extra_space_end', 'vehicle', 'lesson_gap', 'lesson_duration', 'extra_space_end', 'operation_hour']
        extra_kwargs = {'end_time': {'read_only': True}}

class SpecialLessonSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = SpecialLesson
        fields = ['id', 'hire_car_status', 'hire_car_price_paid', 'hire_car_price', 'hire_car_date', 'hire_car_time', 'vehicle', 'user']

    def get_user(self, instance):
        return DefaultUserSerializer(instance.user).data

class GETMonthlyScheduleSerializer(serializers.ModelSerializer):
    day_name = serializers.SerializerMethodField()
    vehicle = serializers.SerializerMethodField()

    class Meta:
        model = MonthlySchedule
        fields = ['id', 'date', 'start_time', 'end_time', 'launch_break_start', 'launch_break_end', 'extra_space_start', 'extra_space_end', 'vehicle', 'day_name', 'lesson_gap', 'lesson_duration', 'extra_space_end', 'operation_hour']
    
    def get_day_name(self, instance):
        return get_day_name(instance.date)
    

    def get_vehicle(self, instance):
        if instance.vehicle:
            return VehicleSerializer(instance.vehicle).data
        return None

class LearnerDataScheduleSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()
    is_ongoing = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    lesson_number = serializers.SerializerMethodField()
    school = serializers.SerializerMethodField()

    class Meta:
        model = LearnerBookingSchedule
        fields = ['id',  'location', 'latitude', 'longitude', 'date', 'slot', 'lesson_name', 'user', 'is_completed', 'is_ongoing', 'vehicle', 'image', 'lesson_number', 'school']
    
    def get_school(self, instance):
        profile, _ = SchoolProfile.objects.get_or_create(user=instance.vehicle.user)
        school_data = SchoolProfileSerializer(profile).data
        return {
            **school_data,
            'full_name': instance.vehicle.user.full_name,
            'logo': instance.vehicle.user.logo.url if instance.vehicle.user.logo else None
        }

    def get_lesson_number(self, instance):

        today = date.today()
        completed_lessons = LearnerBookingSchedule.objects.filter(
            user=instance.user,
            date__lt=today
        ).count()

        if instance.date < today:
            return completed_lessons
        return completed_lessons + 1
    
    def get_is_completed(self, instance):
        today = date.today()
        return instance.date < today

    def get_is_ongoing(self, instance):
        today = date.today()
        return instance.date >= today

    def get_image(self, instance):
        course = Course.objects.filter(user=instance.vehicle.user).first()
        if course and course.lesson.exists():
            lesson = course.lesson.order_by('?').first()
            if lesson and lesson.image:
                domain = getattr(settings, 'DOMAIN', '')
                return f"{domain}{lesson.image.url}"
        return None



    
class GETLearnerBookingScheduleSerializer(serializers.ModelSerializer):
    vehicle = serializers.SerializerMethodField()
    locations = serializers.SerializerMethodField()

    class Meta:
        model = LearnerBookingSchedule
        fields = ['id', 'vehicle', 'locations']

    
    def get_vehicle(self, instance):
        if instance.vehicle:
            return VehicleSerializer(instance.vehicle).data
        else:
            return None
        
    def get_locations(self, instance):
        if instance.vehicle:
            locations = Location.objects.filter(radius__user=instance.vehicle.user)
            return LocationSerializer(locations, many=True).data
        else:
            return None
    
    
class UserLessonSerializer(serializers.ModelSerializer):
    total_lesson = serializers.SerializerMethodField()
    attend_lesson = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    attend_percentage = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'total_lesson', 'start_date', 'attend_lesson', 'attend_percentage']
    
    def get_attend_percentage(self, instance):
        if instance.total_lessons > 0:
            return round((instance.completed_lessons / instance.total_lessons) * 100, 2)
        return 0.0
    
    def get_total_lesson(self, instance):
        return getattr(instance, 'total_lessons', 0)

    def get_attend_lesson(self, instance):
        completed = getattr(instance, 'completed_lessons', 0)
        total = getattr(instance, 'total_lessons', 0)
        return f'{completed}/{total}'

    def get_start_date(self, instance):
        return getattr(instance, 'earliest_lesson_date', None)