from django.urls import path
from . import views
from .views import CreateDepositIntentView, ConfirmDepositView

urlpatterns = [
    path('signup', views.SignUpView.as_view()),
    path('signin', views.SignInView.as_view()),
    path('EmailVerifyView', views.EmailVerifyView.as_view()),
    path('LogoutView', views.LogoutView.as_view()),
    path('updateprofile', views.UserProfileUpdateView.as_view()),
    path('DriverProfileView', views.DriverProfileView.as_view()),
    path('ResendOTPView', views.ResendOTPView.as_view()),
    path('ForgotPasswordView', views.ForgotPasswordView.as_view()),
    path('MobileNumberVerify', views.MobileNumberVerifyAPIView.as_view()),
    path('RatingView', views.RatingView.as_view()),
    path('SocialLogin', views.SocialLoginAPIView.as_view()),
    path('create-deposit/', CreateDepositIntentView.as_view()),
    path('confirm-deposit/', ConfirmDepositView.as_view()),

]
