from django.db import models
from utils_app.models import BaseModelWithCreatedInfo

# Create your models here.
class MonthlySchedule(BaseModelWithCreatedInfo):
    user = models.ForeignKey('user_management_app.User', on_delete=models.CASCADE, related_name='monthlyschedule_user')
    vehicle = models.ForeignKey('course_management_app.Vehicle', on_delete=models.CASCADE, related_name='monthlyschedule_vehicle')
    location =  models.JSONField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    launch_break_start = models.TimeField(null=True, blank=True)
    launch_break_end = models.TimeField(null=True, blank=True)
    extra_space_start = models.TimeField(null=True, blank=True)
    extra_space_end = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user} - {self.date}"