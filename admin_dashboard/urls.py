from django.urls import path
from admin_dashboard.views import *

urlpatterns = [
    path('AdminLogin/', AdminLoginApiView.as_view()),
    path('AdminLogout/', AdminLogoutApiView.as_view()),
    path('AdminUserList', AdminUserListView.as_view()),
    path('AdminIncomeGraph', AdminIncomeGraphAPIView.as_view()),
    path('AdminDashboard', AdminDashboardApiView.as_view()),
    path('UserProfile/<int:id>/',UserProfileView.as_view()),
    path('UserInactive/<int:id>/',UserInactiveApiView.as_view()),
    path('DeleteUser/<int:id>/',AdminDeleteUserApiView.as_view()),
    path('InstituteDetail/<int:id>/',InstituteApprovaldetailApiView.as_view()),
    path('DrivingSchoolList/',DrivingSchoolListAPIView.as_view()),
    path('SchoolStatusUpdate/<int:id>/',DrivingSchoolAPIView.as_view()),
    path('AdminAllLessons/', LessonListAPIView.as_view(), name='lesson-list'),
    path('AdminAddLessons/', AdminAddLessonAPIView.as_view(), name='lesson-detail'),
    path('AdminUpdateLesson/<int:id>/',AdminUpdateLesson.as_view()),
    path('AdminDeleteLesson/<int:id>/',AdminDeleteLesson.as_view()),
    path('AdminDashboardReport/',AdminDashboardReportView.as_view()),

    # Template Base
    path('delete_user_account/',delete_user_account)
]


