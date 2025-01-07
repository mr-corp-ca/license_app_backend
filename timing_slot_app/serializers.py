from rest_framework import serializers
from timing_slot_app.constants import get_day_name
from .models import MonthlySchedule

class MonthlyScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlySchedule
        fields = ['date', 'start_time', 'end_time', 'launch_break_start', 'launch_break_end', 'extra_space_start', 'extra_space_end', 'vehicle', 'lesson_gap', 'lesson_duration', 'extra_space_end', 'operation_hour']

class GETMonthlyScheduleSerializer(serializers.ModelSerializer):
    day_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MonthlySchedule
        fields = ['date', 'start_time', 'end_time', 'launch_break_start', 'launch_break_end', 'extra_space_start', 'extra_space_end', 'vehicle', 'day_name', 'lesson_gap', 'lesson_duration', 'extra_space_end']
    
    def get_day_name(self, instance):
        return get_day_name(instance.date)