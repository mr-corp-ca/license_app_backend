from rest_framework import serializers
from .models import MonthlySchedule

class MonthlyScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlySchedule
        fields = ['date', 'start_time', 'end_time', 'launch_break_start', 'launch_break_end', 'extra_space_start', 'extra_space_end', 'vehicle']
