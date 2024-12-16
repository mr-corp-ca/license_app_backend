from rest_framework import status
from django.core.mail import send_mail
from rest_framework.views import APIView
from user_management_app.constants import sendSMS
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from utils_app.models import City, Province, Radius, Location
from utils_app.serializers import CitySerializer, ProvinceSerializer,CreateRadiusSerializer, RadiusSerializer

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


class RadiusListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        radii = Radius.objects.filter(user=request.user)
        serializer = RadiusSerializer(radii, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = request.user.id
        try:
            locations = request.data.get("locations", [])
            try:
                request.data._mutable = True
            except:
                pass
            request.data['user'] = user
            radius_serializer = CreateRadiusSerializer(data=request.data)
            if radius_serializer.is_valid():
                radius = radius_serializer.save()
                if locations:
                    for loca in locations:
                        Location.objects.create(radius=radius, location_name=loca['location_name'],latitude=loca['latitude'], longitude=loca['latitude'])

                response_data = RadiusSerializer(radius).data
                return Response(response_data, status=status.HTTP_201_CREATED)

            return Response(radius_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request, id):
        try:
            user = request.user
            radius = Radius.objects.filter(id=id).first()
            if not radius:
                return Response({"success": False, "response": {"message": 'Radius object not found!'}}, status=status.HTTP_404_NOT_FOUND)

            radius_serializer = CreateRadiusSerializer(radius, data=request.data, partial=True)  
            if radius_serializer.is_valid():
                updated_radius = radius_serializer.save()

                locations_data = request.data.get("locations", [])
                if locations_data:
                    for loca in locations_data:
                        existing_location = Location.objects.filter(radius=updated_radius, location_name=loca['location_name']).first()
                        
                        if existing_location:
                            existing_location.latitude = loca['latitude']
                            existing_location.longitude = loca['longitude']
                            existing_location.save()
                        else:
                            Location.objects.create(
                                radius=updated_radius,
                                location_name=loca['location_name'],
                                latitude=loca['latitude'],
                                longitude=loca['longitude']
                            )

                response_data = RadiusSerializer(updated_radius).data
                return Response(response_data, status=status.HTTP_200_OK)

            return Response(radius_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
