from rest_framework import status
from django.core.mail import send_mail
from rest_framework.views import APIView
from user_management_app.constants import sendSMS
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from utils_app.models import City, Province
from utils_app.serializers import CitySerializer, ProvinceSerializer

# Create your views here.

class ProvinceApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        province_list = Province.objects.all()
        serializer = ProvinceSerializer(province_list, many=True)
        return Response({'success': True, 'response': {'data': serializer.data}},
                        status=status.HTTP_200_OK)
class CityApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        province = request.GET.get('province', None)
        if not province:
            return Response({"message": "Enter Province for city"}, status=status.HTTP_400_BAD_REQUEST)
        city_list = City.objects.filter(province=province)
        serializer = CitySerializer(city_list, many=True)
        return Response({'success': True, 'response': {'data': serializer.data}},
                        status=status.HTTP_200_OK)