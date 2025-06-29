from django.urls import path
from timing_slot_app.views import *

urlpatterns = [
    path('MonthlySchedule/', MonthlyScheduleAPIView.as_view()),
    path('MonthlyScheduleList/', MonthlyScheduleAPIView.as_view()),
    path('LeanerSchedule',LearnerMonthlyScheduleView.as_view()),
    path('CheckAvailabiltyCar/', SpecialLessonRequestView.as_view()),
    path('MyBookedVehicle', MyBookedVehicleApiView.as_view()),
    path('RequestSpecialLesson', RequestSpecialLessonApiView.as_view()),

]
    


