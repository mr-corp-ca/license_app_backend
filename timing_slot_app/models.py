from django.db import models
from timing_slot_app.constants import LESSON_SELECT_CHOICE,HIRE_CAR_STATUS,ROAD_TEST_STATUS_CHOICES
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
    lesson_gap = models.PositiveIntegerField(null=True, blank=True, default=0, help_text='Lesson gap in minutes')
    lesson_duration = models.PositiveIntegerField(null=True, blank=True, default=0, help_text='Lesson duration in hours')
    shift_timing = models.PositiveIntegerField(null=True, blank=True, default=0, help_text='Shift timing in hours')
    operation_hour = models.PositiveIntegerField(null=True, blank=True, default=0, help_text='Operation time in hours')

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user} - {self.date}"
    

class LearnerBookingSchedule(BaseModelWithCreatedInfo):

    user = models.ForeignKey('user_management_app.User', on_delete=models.CASCADE, related_name='learnerweekly_user')
    vehicle = models.ForeignKey('course_management_app.Vehicle', on_delete=models.CASCADE, related_name='learnerboked_vehicle')
    location =  models.CharField(max_length=500,null=True,blank=True)
    latitude =  models.DecimalField(max_digits=9, decimal_places=6,null=True, blank=True)
    longitude =  models.DecimalField(max_digits=9, decimal_places=6,null=True, blank=True)
    date = models.DateField()

    road_test = models.BooleanField(default= False)
    road_test_date= models.DateField(null=True, blank=True)
    road_test_time = models.TimeField(null=True, blank=True) 
    road_test_status = models.CharField(max_length=10, choices=ROAD_TEST_STATUS_CHOICES, default='pending')
    special_lesson = models.BooleanField(default= False)
    hire_car = models.BooleanField(default= False)
    hire_car_status = models.CharField(max_length=20,choices=HIRE_CAR_STATUS,default='Pending')
    hire_car_price_paid = models.BooleanField(default=False)
    hire_car_date = models.DateField(null=True,  blank=True)
    hire_car_time = models.TimeField(null=True, blank=True)
    
    slot = models.TimeField(null=True,blank=True)
    is_completed = models.BooleanField(default=False)
    lesson_name =  models.TextField(blank=True, null=True, default='Lesson')
    class Meta:
        unique_together = ('user', 'date')
    
    def __str__(self):
        return f"{self.user} - {self.date}"
    

class SpecialLesson(BaseModelWithCreatedInfo):
    user = models.ForeignKey('user_management_app.User', on_delete=models.CASCADE, related_name='specialllesson_user')
    vehicle = models.ForeignKey('course_management_app.Vehicle', on_delete=models.CASCADE, related_name='specialllesson_vehicle')

    road_test = models.BooleanField(default= False)
    road_test_date= models.DateField(null=True, blank=True)
    road_test_time = models.TimeField(null=True, blank=True) 
    road_test_status = models.CharField(max_length=10, choices=ROAD_TEST_STATUS_CHOICES, null=True, blank=True)
    special_lesson = models.BooleanField(default= False)
    hire_car = models.BooleanField(default= False)
    hire_car_status = models.CharField(max_length=20, choices=HIRE_CAR_STATUS, null=True, blank=True)
    hire_car_price_paid = models.BooleanField(default=False)
    hire_car_price = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    hire_car_date = models.DateField(null=True,  blank=True)
    hire_car_time = models.TimeField(null=True, blank=True)