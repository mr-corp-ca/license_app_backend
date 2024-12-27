import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal

from course_management_app.models import Vehicle
from utils_app.models import Location,Radius
from user_management_app.models import Wallet,TransactionHistroy
from datetime import datetime, timedelta
from utils_app.serializers import LocationSerializer
from .models import MonthlySchedule,LearnerBookingSchedule
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
            vehicle_id = request.query_params.get('vehicle_id')
            current_location_name = request.query_params.get('current_location')

            vehicle = Vehicle.objects.filter(id=vehicle_id).first()
            if not vehicle:
                return Response({'success': False, 'message': 'Vehicle ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                monthly_schedules = MonthlySchedule.objects.filter(vehicle_id=vehicle_id)
                booked_slots = LearnerBookingSchedule.objects.filter(vehicle_id=vehicle_id).values_list("slot", flat=True)
                booked_slots = [slot.strftime("%H:%M") for slot in booked_slots]

                available_slots = []
                for schedule in monthly_schedules:
                    start_time = schedule.start_time
                    end_time = schedule.end_time
                    lunch_break_start = schedule.launch_break_start
                    lunch_break_end = schedule.launch_break_end

                    if start_time.strftime("%H:%M") not in booked_slots and \
                        (not lunch_break_start or start_time < lunch_break_start or start_time >= lunch_break_end) and \
                        start_time != end_time:
                        available_slots.append(start_time.strftime("%H:%M"))

                locations = Location.objects.filter(radius__user=vehicle.user)
                serialized_locations = LocationSerializer(locations, many=True).data

                return Response({
                    'success': True,
                    'available_slots': available_slots,
                    'locations': serialized_locations,
                    'current_location_option': {
                        'location_name': current_location_name,
                        'additional_charge': 10.00
                    }
                }, status=status.HTTP_200_OK)

            except MonthlySchedule.DoesNotExist:
                return Response({'success': False, 'message': 'No schedule found for the given vehicle.'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
 
    def post(self, request):
        try:
            user = request.user
            data = request.data
            selected_location = data.get('selected_location')
            current_location = data.get('current_location', False)

            if not selected_location:
                return Response({'success': False, 'message': 'Please select a location.'}, status=status.HTTP_400_BAD_REQUEST)

            if current_location:
                current_location_latitude = data.get('latitude')
                current_location_longitude = data.get('longitude')

                if not current_location_latitude or not current_location_longitude:
                    return Response({'success': False, 'message': 'Latitude and longitude are required for current location.'}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    wallet = Wallet.objects.get(user=user)
                except Wallet.DoesNotExist:
                    return Response({'success': False, 'message': 'Wallet not found for the user.'}, status=status.HTTP_404_NOT_FOUND)

                amount_to_debit = Decimal('10.00')

                if wallet.balance < amount_to_debit:
                    return Response({'success': False, 'message': 'Insufficient wallet balance.'}, status=status.HTTP_400_BAD_REQUEST)

                wallet.balance -= amount_to_debit
                wallet.save()

                TransactionHistroy.objects.create(
                    wallet=wallet,
                    amount=amount_to_debit,
                    transaction_type="DEBIT"
                )
            else:
                location = Location.objects.filter(id=selected_location).first()
                if not location:
                    return Response({'success': False, 'message': 'Selected location does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
                selected_location = location.location_name
                current_location_latitude = location.latitude
                current_location_longitude = location.longitude

            vehicle = Vehicle.objects.filter(id=data.get('vehicle_id')).first()
            if not vehicle:
                return Response({'success': False, 'message': 'Vehicle not found.'}, status=status.HTTP_400_BAD_REQUEST)

            learner_booking = LearnerBookingSchedule.objects.create(
                user=user,
                vehicle=vehicle,  
                location=selected_location,
                latitude=current_location_latitude,
                longitude=current_location_longitude,
                lesson_slection=data.get('lesson_slection'),
                date=data.get('date'),
                slot=data.get('slot'),
                road_test=data.get('road_test', False)
            )

            return Response({'success': True, 'message': 'Location and time slot successfully booked.'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
