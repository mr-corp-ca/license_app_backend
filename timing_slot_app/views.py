import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from course_management_app.models import  Vehicle
from utils_app.models import  Location, Radius
from utils_app.serializers import LocationSerializer
from .models import MonthlySchedule
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from .serializers import MonthlyScheduleSerializer

class MonthlyScheduleAPIView(APIView):
    def patch(self, request):
        serializer = MonthlyScheduleSerializer(data=request.data, many=True)
        if serializer.is_valid():
            for item in serializer.validated_data:
                item['user'] = request.user
                schedule, created = MonthlySchedule.objects.update_or_create(
                    user=request.user, 
                    date=item['date'], 
                    defaults=item
                )
            return Response(
                {"success": True, "response": {"data": serializer.data}},
                status=status.HTTP_201_CREATED
            )
        else:
            first_error = serializer.errors[0] 
            first_field, errors = next(iter(first_error.items()))
            formatted_field = " ".join(word.capitalize() for word in first_field.split("_"))
            first_error_message = f"{formatted_field} is required!" 
            return Response(
                {'success': False, 'response': {'message': first_error_message}},
                status=status.HTTP_400_BAD_REQUEST
            )


class LearnerMonthlyScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        schedules = MonthlySchedule.objects.filter(user=user).order_by('date')
        schedule_serializer = MonthlyScheduleSerializer(schedules, many=True)

        return Response({
            'success': True,
            'schedules': schedule_serializer.data
        }, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request):
        """Create or update a schedule for the learner."""
        data = request.data
        user = request.user

        vehicle_id = data.get('vehicle_id')
        vehicle = Vehicle.objects.filter(id=vehicle_id).first()
        if not vehicle:
            return Response({'success': False, 'message': 'Invalid or unassigned vehicle.'}, status=status.HTTP_400_BAD_REQUEST)

        current_location = data.get('current_location') 

        schedules = data.get('schedules', [])
        for schedule_data in schedules:
            date = schedule_data.get('date')
            start_time = schedule_data.get('start_time')
            end_time = schedule_data.get('end_time')
            launch_break_start = schedule_data.get('launch_break_start')
            launch_break_end = schedule_data.get('launch_break_end')
            extra_space_start = schedule_data.get('extra_space_start')
            extra_space_end = schedule_data.get('extra_space_end')

            if not date or not start_time or not end_time:
                return Response({
                    'success': False,
                    'message': 'Date, start_time, and end_time are required for scheduling.'
                }, status=status.HTTP_400_BAD_REQUEST)

            locations = []
            for location_data in schedule_data.get('locations', []): 
                location_name = location_data.get('location_name')
                latitude = location_data.get('latitude')
                longitude = location_data.get('longitude')

                location = {
                    'location_name': location_name,
                    'latitude': latitude,
                    'longitude': longitude
                }

                if current_location:
                    if self.is_within_radius(current_location, location):
                        pass # Add $10 charge for location match

                locations.append(location)

            if not locations:
                return Response({
                    'success': False,
                    'message': 'No valid locations found.'
                }, status=status.HTTP_400_BAD_REQUEST)

            MonthlySchedule.objects.update_or_create(
                user=user,
                date=date,
                defaults={
                    'vehicle': vehicle,
                    'location': locations,  
                    'start_time': start_time,
                    'end_time': end_time,
                    'launch_break_start': launch_break_start,
                    'launch_break_end': launch_break_end,
                    'extra_space_start': extra_space_start,
                    'extra_space_end': extra_space_end,
                }
            )

        return Response({'success': True, 'message': 'Schedule updated successfully.'}, status=status.HTTP_200_OK)

    def delete(self, request):
        """Delete a schedule by date."""
        date = request.data.get('date')
        if not date:
            return Response({'success': False, 'message': 'Date is required to delete a schedule.'}, status=status.HTTP_400_BAD_REQUEST)

        schedule = MonthlySchedule.objects.filter(user=request.user, date=date).first()
        if not schedule:
            return Response({'success': False, 'message': 'Schedule not found for the given date.'}, status=status.HTTP_404_NOT_FOUND)

        schedule.delete()
        return Response({'success': True, 'message': 'Schedule deleted successfully.'}, status=status.HTTP_200_OK)

    def is_within_radius(self, current_location, location):
        """
        Check if the current location is within a certain radius of the provided location.
        For simplicity, let's assume a dummy condition here.
        """
        # Dummy logic: checking if the locations are the same
        if current_location['latitude'] == location['latitude'] and current_location['longitude'] == location['longitude']:
            return True
        return False