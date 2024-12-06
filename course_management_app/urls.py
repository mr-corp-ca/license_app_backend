from django.urls import path
from course_management_app.views import *

urlpatterns = [
    path('CreateCourse', CourseApiView.as_view()),
    path('EditCourse/<int:id>', CourseApiView.as_view()),
    path('DeleteCourse/<int:id>', CourseApiView.as_view()),
    path('MyCourse', CourseApiView.as_view()),

    path('ServicesList', ServicesApiView.as_view()),
    path('LicenseCategoryList', LicenseCategoryApiView.as_view()),

    path('CreatePackage/', PackageApiView.as_view()),
    path('MyPackage', PackageApiView.as_view()),
    path('DeletePackage/<int:id>', PackageApiView.as_view()),

    path('CreateDiscountOffer/', DiscountOfferApiView.as_view()),
    path('MyDiscountOffer', DiscountOfferApiView.as_view()),
    path('EditDiscountOffer/<int:id>', DiscountOfferApiView.as_view()),
    path('DeleteDiscountOffer/<int:id>', DiscountOfferApiView.as_view()),

]
