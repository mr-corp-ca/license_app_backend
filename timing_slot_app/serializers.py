from course_management_app.serializers import VehicleSerializer
from rest_framework import serializers
from timing_slot_app.constants import get_day_name
from user_management_app.models import User
from user_management_app.serializers import DefaultUserSerializer
from utils_app.models import Location
from utils_app.serializers import LocationSerializer
from .models import LearnerBookingSchedule, MonthlySchedule, SpecialLesson

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