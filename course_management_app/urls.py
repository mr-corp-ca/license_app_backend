from django.urls import path
from course_management_app.views import *

urlpatterns = [
    path('CreateCourse', CourseApiView.as_view()),
    path('EditCourse/<int:id>', CourseApiView.as_view()),
    path('DeleteCourse/<int:id>', CourseApiView.as_view()),
    path('MyCourse', CourseApiView.as_view()),

    path('ServicesList', ServicesApiView.as_view()),
    path('LicenseCategoryList', LicenseCategoryApiView.as_view()),

]
