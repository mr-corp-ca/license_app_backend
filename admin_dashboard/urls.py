from django.urls import path
from admin_dashboard.views import AdminDashboardApiView, AdminIncomeGraphAPIView, AdminLoginApiView, AdminLogoutApiView, AdminUserListView

urlpatterns = [
    path('AdminLogin/', AdminLoginApiView.as_view()),
    path('AdminLogout/', AdminLogoutApiView.as_view()),
    path('AdminUserList', AdminUserListView.as_view()),
    path('AdminIncomeGraph', AdminIncomeGraphAPIView.as_view()),
    path('AdminDashboard', AdminDashboardApiView.as_view()),

]