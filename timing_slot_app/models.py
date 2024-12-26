from django.db import models
from utils_app.models import BaseModelWithCreatedInfo

# Create your models here.
class MonthlySchedule(BaseModelWithCreatedInfo):
    user = models.ForeignKey('user_management_app.User', on_delete=models.CASCADE, related_name='monthlyschedule_user')
    vehicle = models.ForeignKey('course_management_app.Vehicle', on_delete=models.CASCADE, related_name='monthlyschedule_vehicle')
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
    

class LearnerBookingSchedule(BaseModelWithCreatedInfo):
    LESSON_SELECT_CHOICE =(
        ('i need a special lesson','I Need a special lesson'),
        ('i want to hire a car','I want to hire a car'),
    )
    user = models.ForeignKey('user_management_app.User', on_delete=models.CASCADE, related_name='learnerweekly_user')
    vehicle = models.ForeignKey('course_management_app.Vehicle', on_delete=models.CASCADE, related_name='learnerboked_vehicle')
    location =  models.CharField(max_length=255,null=True,blank=True)
    latitude =  models.DecimalField(max_digits=9, decimal_places=6,null=True, blank=True)
    longitude =  models.DecimalField(max_digits=9, decimal_places=6,null=True, blank=True)
    lesson_slection = models.CharField(max_length=50, null=True, blank=True, choices=LESSON_SELECT_CHOICE, verbose_name='Lesson Selection')
    date = models.DateField()
    road_test = models.BooleanField(default= False)
    slot = models.TimeField(null=True,blank=True)
    class Meta:
        unique_together = ('user', 'date')
    
    def __str__(self):
        return f"{self.user} - {self.date}"