from course_management_app.serializers import VehicleSerializer
from rest_framework import serializers
from timing_slot_app.constants import get_day_name
from utils_app.models import Location
from utils_app.serializers import LocationSerializer
from .models import LearnerBookingSchedule, MonthlySchedule

class MonthlyScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlySchedule
        fields = ['date', 'start_time', 'end_time', 'launch_break_start', 'launch_break_end', 'extra_space_start', 'extra_space_end', 'vehicle', 'lesson_gap', 'lesson_duration', 'extra_space_end', 'operation_hour']
        extra_kwargs = {'end_time': {'read_only': True}}

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
    
    