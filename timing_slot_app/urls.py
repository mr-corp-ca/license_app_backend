from django.urls import path
from timing_slot_app.views import *

urlpatterns = [
    path('MonthlySchedule/', MonthlyScheduleAPIView.as_view()),
    path('LeanerSchedule',LearnerMonthlyScheduleView.as_view())
]
    


