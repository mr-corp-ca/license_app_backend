from django.urls import path
from user_management_app.views import *

urlpatterns = [
    path('signin/', SignInView.as_view()),
    path('verify_otp/', VerifyOTPView.as_view()),
    path('Logout', LogoutApiView.as_view()),
    path('get_profile', UserApiView.as_view()),
    path('EditProfile/', UserApiView.as_view()),
    path('SocialLogin/', SocialLoginApiView.as_view()),

    path('signup/', UserApiView.as_view()),
    path('DriverProfileView/', DriverProfileView.as_view()),
    path('ResendOTPView/', ResendOTPView.as_view()),
    path('ForgotPasswordView/', ForgotPasswordView.as_view()),
    path('MobileNumberVerify/', MobileNumberVerifyAPIView.as_view()),
    path('RatingView/', RatingView.as_view()),
    path('UserNotification/', UserNotificationAPIView.as_view()),
    # path('SearchSchool/',SearchSchool.as_view()),
    path('schoolDetail/<int:id>/',SchoolDetail.as_view()),
    path('schools/<int:id>/vehicles/', VehicleSelectionView.as_view(), name='vehicle-selection'),
    path('NewLearnerDetail/<int:id>/',LearnerDetailApiview.as_view()),
    path('SchoolRatingList/',SchoolRatingListAPIView.as_view()),
    path('PaymentDetail/<int:id>/',PaymentDetailView.as_view()),
    path('PaymentRequest/',PaymentRequestView.as_view()),
    path('CancleReport/',LearnerReportAPIVIEW.as_view())
]
