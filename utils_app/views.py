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
            return Response({'success':False,'response':{"message": "Enter Province for city"}}, status=status.HTTP_400_BAD_REQUEST)
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
            if hasattr(request.data, "_mutable"):
                request.data._mutable = True

            # Add user ID to request data
            request.data["user"] = user

            # Extract main location data if needed
            main_location_name = request.data.get("main_location_name", "").strip()
            main_latitude = request.data.get("main_latitude", "").strip()
            main_longitude = request.data.get("main_longitude", "").strip()

            # Handle locations data dynamically
            locations = []
            for key, value in request.data.items():
                if key.startswith("locations[") and key.endswith("][location_name]"):
                    index = key.split("[")[1].split("]")[0]
                    location_data = {
                        "location_name": request.data.get(f"locations[{index}][location_name]", "").strip(),
                        "latitude": request.data.get(f"locations[{index}][latitude]", "").strip(),
                        "longitude": request.data.get(f"locations[{index}][longitude]", "").strip(),
                    }
                    locations.append(location_data)

            # Prepare data for serializer
            radius_serializer = CreateRadiusSerializer(data=request.data)
            if radius_serializer.is_valid():
                radius = radius_serializer.save()

                # Save locations if they exist
                if locations:
                    for loca in locations:
                        Location.objects.create(
                            radius=radius,
                            location_name=loca["location_name"],
                            latitude=loca["latitude"],
                            longitude=loca["longitude"]
                        )

                # Serialize the saved radius data
                response_data = RadiusSerializer(radius).data
                return Response(
                {"success": True, "response": {"data": response_data}},
                status=status.HTTP_201_CREATED
            )
            else:
            # Extract and format the first error
                first_field, errors = next(iter(radius_serializer.errors.items()))
                formatted_field = " ".join(word.capitalize() for word in first_field.split("_"))
                first_error_message = f"{formatted_field} is required!"
                return Response(
                    {'success': False, 'response': {'message': first_error_message}},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
                return Response(
                    {'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST
                )

        
    def patch(self, request, id):
        try:
            user = request.user
            radius = Radius.objects.filter(id=id).first()
            if not radius:
                return Response({"success": False, "response": {"message": 'Radius object not found!'}}, status=status.HTTP_404_NOT_FOUND)
            
            locations = []
            for key, value in request.data.items():
                if key.startswith("locations[") and key.endswith("][location_name]"):
                    index = key.split("[")[1].split("]")[0]
                    location_data = {
                        "location_name": request.data.get(f"locations[{index}][location_name]", "").strip(),
                        "latitude": request.data.get(f"locations[{index}][latitude]", "").strip(),
                        "longitude": request.data.get(f"locations[{index}][longitude]", "").strip(),
                    }
                    locations.append(location_data)

            radius_serializer = CreateRadiusSerializer(radius, data=request.data, partial=True)  
            if radius_serializer.is_valid():
                radius = radius_serializer.save()

                if locations:
                    Location.objects.filter(radius=radius).delete()
                    for loca in locations:
                        Location.objects.create(
                            radius=radius,
                            location_name=loca["location_name"],
                            latitude=loca["latitude"],
                            longitude=loca["longitude"]
                        )
                response_data = RadiusSerializer(radius).data
                return Response(
                {"success": True, "response": {"data": response_data}},
                status=status.HTTP_201_CREATED
            )
            else:
                first_field, errors = next(iter(radius_serializer.errors.items()))
                formatted_field = " ".join(word.capitalize() for word in first_field.split("_"))
                first_error_message = f"{formatted_field} is required!"
                return Response(
                    {'success': False, 'response': {'message': first_error_message}},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
                return Response(
                    {'success': False, 'response': {'message': str(e)}},
                    status=status.HTTP_400_BAD_REQUEST
                )