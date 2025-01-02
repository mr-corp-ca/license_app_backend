from django.urls import path
from course_management_app.views import *

urlpatterns = [
    path('CreateCourse', CourseApiView.as_view()),
    path('EditCourse/<int:id>', CourseApiView.as_view()),
    path('DeleteCourse/<int:id>', CourseApiView.as_view()),
    path('MyCourse', CourseApiView.as_view()),

    path('Alllessons',LessonApiView.as_view()),
    path('ServicesList', ServicesApiView.as_view()),
    path('LicenseCategoryList', LicenseCategoryApiView.as_view()),

    path('CreatePackage/', PackageApiView.as_view()),
    path('MyPackage', PackageApiView.as_view()),
    path('DeletePackage/<int:id>', PackageApiView.as_view()),

    path('CreateDiscountOffer/', DiscountOfferApiView.as_view()),
    path('MyDiscountOffer', DiscountOfferApiView.as_view()),
    path('EditDiscountOffer/<int:id>', DiscountOfferApiView.as_view()),
    path('DeleteDiscountOffer/<int:id>', DiscountOfferApiView.as_view()),

    path('Generalpolicy',PolicyApiview.as_view()),
    path('certificates/', CertificateCreateAPIView.as_view()),
    path('certificates/<int:id>/', CertificateCreateAPIView.as_view()),

    path('AddVehicle',AddVehicleApiView.as_view(),name= 'add-vehicle'),

    path('learner-list', LearnerListAPIView.as_view()),
    path('SchoolPackageDetail/<int:id>', SchoolPackageDetailAPIView.as_view()),
    path('CoursesList', CoursesListAPIView.as_view()),

]

