from django.urls import path
from utils_app.views import *

urlpatterns = [
    path('CityList', CityApiView.as_view()),
    path('ProvinceList', ProvinceApiView.as_view()),

    path('MyRadiusList', RadiusListCreateView.as_view(), name='radius-list'), 
    path('EditRadiusList/<int:id>/', RadiusListCreateView.as_view(), name='radius-edit'),  
]
