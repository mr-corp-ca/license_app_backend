import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from datetime import date
from course_management_app.models import Vehicle
from timing_slot_app.constants import get_day_name, get_schedule_times
from utils_app.models import Location,Radius
from user_management_app.models import Wallet,TransactionHistroy
from datetime import datetime, timedelta
from utils_app.serializers import LocationSerializer
from .models import MonthlySchedule,LearnerBookingSchedule
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from .serializers import GETMonthlyScheduleSerializer, MonthlyScheduleSerializer

class MonthlyScheduleAPIView(APIView):
    def post(self, request):
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

    def get(self, request):
        user = request.user
        schedule_objects = MonthlySchedule.objects.filter(user=user).order_by('date')
        serializer = GETMonthlyScheduleSerializer(schedule_objects, many=True)
        return Response(
            {"success": True, "response": {"data": serializer.data}},
            status=status.HTTP_200_OK
        )
class LearnerMonthlyScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
            user = request.user
            vehicle_id = request.query_params.get('vehicle_id')
            current_location_name = request.query_params.get('current_location')

            if not vehicle_id:
                return Response(
                        {'success': False, 'response': {'message': 'Vehicle ID is required.'}},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            vehicle = Vehicle.objects.filter(id=vehicle_id).first()
            if not vehicle:
                return Response(
                        {'success': False, 'response': {'message': 'Vehicle not found!.'}},
                        status=status.HTTP_404_NOT_FOUND
                    )
            try:
                locations = Location.objects.filter(radius__user=vehicle.user)
                serialized_locations = LocationSerializer(locations, many=True).data
                
                monthly_schedules = MonthlySchedule.objects.filter(vehicle_id=vehicle_id)
                booked_slots = LearnerBookingSchedule.objects.filter(vehicle_id=vehicle_id).values_list("slot", flat=True)

                booked_slots = [slot.strftime("%H:%M") for slot in booked_slots]

                available_slots = []
                for schedule in monthly_schedules:
                    available_slots.append({'slot':get_schedule_times(schedule), 'date':schedule.date, 'day_name':get_day_name(schedule.date)})


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
                return Response(
                        {'success': False, 'response': {'message': 'No schedule found for the given vehicle.'}},
                        status=status.HTTP_404_NOT_FOUND
                    )
            except Exception as e:
                    return Response(
                        {'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )


    def post(self, request):
        try:
            user = request.user
            data = request.data

            if isinstance(data, list):
                response_list = []

                for item in data:
                    response = self.process_booking(user, item)
                    response_list.append(response)
                    if not response.get('success'):
                        return Response(
                            {'success': False, 'response': response.get('message')},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                return Response({'success': True, 'response': response_list[0]}, status=status.HTTP_201_CREATED)

            else:
                return Response(
                    {'success': False, 'response': {'message': 'Invalid data format. Expected a dictionary or list.'}},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return Response({'success': False, 'response': {'message': str(e)}}, status=status.HTTP_400_BAD_REQUEST)

    def process_booking(self, user, data):
        try:
            selected_location = data.get('selected_location')
            current_location = data.get('current_location', False)
            current_date = date.today()
            date_str = data.get('date')

            last_monthly_obj = MonthlySchedule.objects.all().order_by('-date').first()
            try:
                input_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return {'success': False, 'message': 'Invalid date format. Please use YYYY-MM-DD.'}

            if not last_monthly_obj:
                return {'success': False, 'message': 'No monthly schedule available.'}

            if input_date < current_date:
                return {'success': False, 'message': 'The date should be later than the current date.'}

            if input_date > last_monthly_obj.date:
                return {
                    'success': False,
                    'message': f"The date should be earlier than {last_monthly_obj.date.strftime('%Y-%m-%d')}"
                }

            if not selected_location:
                return {'success': False, 'message': 'Please select a location.'}

            if current_location:
                current_location_latitude = data.get('latitude')
                current_location_longitude = data.get('longitude')

                if not current_location_latitude or not current_location_longitude:
                    return {'success': False, 'message': 'Latitude and longitude are required for current location.'}

                try:
                    wallet = Wallet.objects.get(user=user)
                except Wallet.DoesNotExist:
                    return {'success': False, 'message': 'Wallet not found for the user.'}

                amount_to_debit = Decimal('10.00')

                if wallet.balance < amount_to_debit:
                    return {'success': False, 'message': 'Insufficient wallet balance.'}

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
                    return {'success': False, 'message': 'Selected location does not exist.'}
                selected_location = location.location_name
                current_location_latitude = location.latitude
                current_location_longitude = location.longitude

            vehicle = Vehicle.objects.filter(id=data.get('vehicle_id')).first()
            if not vehicle:
                return {'success': False, 'message': 'Vehicle not found.'}

            LearnerBookingSchedule.objects.update_or_create(
                user=user,
                vehicle=vehicle,
                date=data.get('date'),
                defaults={
                    'location': selected_location,
                    'latitude': current_location_latitude,
                    'longitude': current_location_longitude,
                    'slot': data.get('slot'),
                    'road_test': data.get('road_test', False),
                }
            )

            return {'success': True, 'message': 'Location and time slot successfully booked.'}

        except Exception as e:
            return {'success': False, 'message': str(e)}