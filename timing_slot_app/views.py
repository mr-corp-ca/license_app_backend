import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from datetime import date
from course_management_app.models import Vehicle
from timing_slot_app.constants import calculate_end_time, get_day_name, get_schedule_times, validate_even_or_odd,convert_time
from utils_app.models import Location,Radius
from user_management_app.models import Wallet,TransactionHistroy
from datetime import datetime, timedelta, time
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
                try:
                    date_str = item['date'].strftime('%Y-%m-%d')
                    
                    # Calculate end_time based on operation_hour if provided
                    if 'operation_hour' in item and item['operation_hour']:
                        operation_hours = int(item['operation_hour'])
                        start_datetime = datetime.combine(item['date'], item['start_time'])
                        end_datetime = start_datetime + timedelta(hours=operation_hours)
                        item['end_time'] = end_datetime.time()
                    else:
                        item['end_time'] = item.get('end_time', item['start_time'])

                    # Calculate all lesson time slots
                    lesson_slots = self.calculate_lesson_slots(item)

                    # Validate breaks against lessons
                    if item.get('launch_break_start') and item.get('launch_break_end'):
                        self.validate_break_time(
                            item['launch_break_start'],
                            item['launch_break_end'],
                            lesson_slots,
                            "Launch break",
                            date_str
                        )

                    # Validate extra spaces against lessons
                    if item.get('extra_space_start') and item.get('extra_space_end'):
                        self.validate_break_time(
                            item['extra_space_start'],
                            item['extra_space_end'],
                            lesson_slots,
                            "Extra space",
                            date_str
                        )

                    # Validate breaks and extra spaces don't overlap
                    if (item.get('launch_break_start') and item.get('launch_break_end') and
                        item.get('extra_space_start') and item.get('extra_space_end')):
                        self.validate_no_overlap(
                            item['launch_break_start'],
                            item['launch_break_end'],
                            item['extra_space_start'],
                            item['extra_space_end'],
                            "Launch break",
                            "Extra space",
                            date_str
                        )

                    # Validate all time slots are within schedule bounds
                    self.validate_time_bounds(item, date_str)

                    # Save the schedule
                    item['user'] = request.user
                    MonthlySchedule.objects.update_or_create(
                        user=request.user, 
                        date=item['date'], 
                        defaults=item
                    )

                except ValueError as e:
                    return Response(
                        {
                            'success': False,
                            'message': str(e),
                            'date': date_str,
                            'available_times': getattr(e, 'available_times', None)
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(
                {"success": True, "message": "Monthly schedule successfully saved"},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'success': False, 'message': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

    def calculate_lesson_slots(self, item):
        """Calculate all possible lesson slots based on schedule, including gaps"""
        lesson_slots = []
        if not item.get('lesson_duration'):
            return lesson_slots

        lesson_duration = item['lesson_duration']
        lesson_gap = item.get('lesson_gap', 0)
        current_time = item['start_time']
        end_time = item['end_time']

        while True:
            lesson_end = (datetime.combine(datetime.today(), current_time) + 
                        timedelta(hours=lesson_duration)).time()
            
            if lesson_end > end_time:
                break
            
            lesson_slots.append({
                'type': 'lesson',
                'start': current_time,
                'end': lesson_end,
                'formatted': f"{current_time.strftime('%H:%M')}-{lesson_end.strftime('%H:%M')}"
            })
            
            if lesson_gap > 0:
                gap_end = (datetime.combine(datetime.today(), lesson_end) + 
                         timedelta(minutes=lesson_gap)).time()
                
                if gap_end <= end_time:
                    lesson_slots.append({
                        'type': 'gap',
                        'start': lesson_end,
                        'end': gap_end,
                        'formatted': f"{lesson_end.strftime('%H:%M')}-{gap_end.strftime('%H:%M')} (gap)"
                    })
                    current_time = gap_end
                else:
                    break
            else:
                current_time = lesson_end
            
            if current_time >= end_time:
                break
        
        return lesson_slots

    def validate_break_time(self, break_start, break_end, lesson_slots, break_name, date_str):
        """
        Validate break/extra space time against lessons
        Allows break to start exactly when lesson ends
        """
        # Get all lesson end times as valid break start times
        valid_start_times = [slot['end'] for slot in lesson_slots if slot['type'] == 'lesson']
        
        # Check if break starts at a lesson end time
        starts_at_lesson_end = any(break_start == end_time for end_time in valid_start_times)
        
        # If break doesn't start at a lesson end, check if it's valid
        if not starts_at_lesson_end:
            # Check if break starts at the beginning of the schedule
            if lesson_slots and break_start == lesson_slots[0]['start']:
                starts_at_lesson_end = True
            else:
                available_starts = [t.strftime('%H:%M') for t in valid_start_times]
                error = ValueError(
                    f"On {date_str}: {break_name} must start when a lesson ends. "
                    f"Available start times: {', '.join(available_starts)}"
                )
                error.available_times = available_starts
                raise error
        
        # Check if break overlaps with any lessons
        for slot in lesson_slots:
            if slot['type'] == 'lesson':  # Only check against lessons, not gaps
                # Allow break to start exactly when lesson ends
                if break_start == slot['end']:
                    continue
                if not (break_end <= slot['start'] or break_start >= slot['end']):
                    available_starts = [t.strftime('%H:%M') for t in valid_start_times]
                    error = ValueError(
                        f"On {date_str}: {break_name} overlaps with lesson {slot['formatted']}. "
                        f"Available start times: {', '.join(available_starts)}"
                    )
                    error.available_times = available_starts
                    raise error

    def validate_no_overlap(self, start1, end1, start2, end2, name1, name2, date_str):
        """Validate two time ranges don't overlap"""
        if not (end1 <= start2 or end2 <= start1):
            raise ValueError(
                f"On {date_str}: {name1} and {name2} overlap"
            )

    def validate_time_bounds(self, item, date_str):
        """Validate all time elements are within schedule bounds"""
        schedule_start = item['start_time']
        schedule_end = item['end_time']

        if item.get('launch_break_start') and item.get('launch_break_end'):
            if (item['launch_break_start'] < schedule_start or 
                item['launch_break_end'] > schedule_end or
                item['launch_break_start'] >= item['launch_break_end']):
                raise ValueError(
                    f"On {date_str}: Launch break must be within scheduled hours "
                    f"({schedule_start.strftime('%H:%M')}-{schedule_end.strftime('%H:%M')})"
                )

        if item.get('extra_space_start') and item.get('extra_space_end'):
            if (item['extra_space_start'] < schedule_start or 
                item['extra_space_end'] > schedule_end or
                item['extra_space_start'] >= item['extra_space_end']):
                raise ValueError(
                    f"On {date_str}: Extra space must be within scheduled hours "
                    f"({schedule_start.strftime('%H:%M')}-{schedule_end.strftime('%H:%M')})"
                )

    def get_available_break_times(self, item):
        """Calculate available times for breaks/extra spaces that don't conflict with lessons"""
        lesson_slots = self.calculate_lesson_slots(item)
        available_slots = []
        
        # If no lessons, the whole schedule is available
        if not lesson_slots:
            return [f"{item['start_time'].strftime('%H:%M')}-{item['end_time'].strftime('%H:%M')}"]
        
        # Check time before first lesson
        first_lesson_start = lesson_slots[0]['start']
        if item['start_time'] < first_lesson_start:
            available_slots.append(f"{item['start_time'].strftime('%H:%M')}-{first_lesson_start.strftime('%H:%M')}")
        
        # Check times between lessons
        for i in range(len(lesson_slots)-1):
            current_end = lesson_slots[i]['end']
            next_start = lesson_slots[i+1]['start']
            if current_end < next_start:
                available_slots.append(f"{current_end.strftime('%H:%M')}-{next_start.strftime('%H:%M')}")
        
        # Check time after last lesson
        last_lesson_end = lesson_slots[-1]['end']
        if last_lesson_end < item['end_time']:
            available_slots.append(f"{last_lesson_end.strftime('%H:%M')}-{item['end_time'].strftime('%H:%M')}")
        
        return available_slots if available_slots else ["No available time slots"]
    
    def get(self, request):
        print("Received Query Params:", request.query_params)
        date = request.query_params.get('date')
        start_time = request.query_params.get('start_time')
        operation_hour = request.query_params.get('operation_hour')
        lesson_duration = request.query_params.get('lesson_duration')

        if not date or not start_time or not operation_hour or not lesson_duration:
            return Response(
                {'success': False, 'response': {'message': 'Missing required parameters'}},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Convert the date string to a date object
            date = datetime.strptime(date, "%Y-%m-%d").date()
            start_time = datetime.strptime(start_time, "%H:%M").time()
            operation_hour = int(operation_hour)
            lesson_duration = int(lesson_duration)
        except ValueError:
            return Response(
                {'success': False, 'response': {'message': 'Invalid parameter format'}},
                status=status.HTTP_400_BAD_REQUEST
            )

        lesson_gap = int(request.query_params.get('lesson_gap', 0))
        launch_break_start = request.query_params.get('launch_break_start')
        launch_break_end = request.query_params.get('launch_break_end')
        extra_space_start = request.query_params.get('extra_space_start')
        extra_space_end = request.query_params.get('extra_space_end')

        launch_break_start = convert_time(launch_break_start)
        launch_break_end = convert_time(launch_break_end)
        extra_space_start = convert_time(extra_space_start)
        extra_space_end = convert_time(extra_space_end)

        schedule_data = calculate_end_time(
            start_time, operation_hour, lesson_duration, lesson_gap,
            launch_break_start, launch_break_end, extra_space_start, extra_space_end
        )

        # Calculate the day name based on the provided date
        day_name = get_day_name(date)

        # Add day name to the schedule data
        schedule_data['day_name'] = day_name

        return Response(
            {"success": True, "response": {"data": schedule_data}},
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
                radius = Radius.objects.filter(user=vehicle.user).first()
                if not radius:
                    return Response(
                        {'success': False, 'response': {'message': 'No radius found for this user.'}},
                        status=status.HTTP_404_NOT_FOUND
                    )

                locations = Location.objects.filter(radius=radius)
                if not locations:
                    return Response(
                        {'success': False, 'response': {'message': 'No locations found for this radius.'}},
                        status=status.HTTP_404_NOT_FOUND
                    )

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
            hire_car_time = data.get('hire_car_time')
            hire_car = data.get('hire_car')
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
            vehicle = Vehicle.objects.filter(id=data.get('vehicle_id')).first()
            if not vehicle:
                return {'success': False, 'message': 'Vehicle not found.'}
            
            if hire_car:
                monthly_schedules = MonthlySchedule.objects.filter(vehicle=vehicle)
                booked_slots = LearnerBookingSchedule.objects.filter(vehicle=vehicle).values_list("slot", flat=True)
                booked_slots = [slot.strftime("%H:%M") for slot in booked_slots]
                available_slots = []
                for schedule in monthly_schedules:
                    available_slots.append({'slot':get_schedule_times(schedule), 'date':schedule.date, 'day_name':get_day_name(schedule.date)})
                
                is_slot_available = any(hire_car_time == slot['slot'] for slot in available_slots)
                if not is_slot_available:
                    return {'success': False, 'message': 'Slot not avaible request for special class!'}
                
                # Pending Payment
                
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



            LearnerBookingSchedule.objects.update_or_create(
                user=user,
                vehicle=vehicle,
                date=data.get('date'),
                defaults={
                    'location': selected_location,
                    'latitude': current_location_latitude,
                    'longitude': current_location_longitude,
                    'road_test': data.get('road_test', False),
                    'hire_car': data.get('hire_car', False),
                    'road_test_date': data.get('road_test_date') if data.get('road_test_date') else None,
                    'road_test_time': data.get('road_test_time') if data.get('road_test_time') else None,
                    'hire_car_date': data.get('hire_car_date') if data.get('hire_car_date') else None,
                    'hire_car_time': data.get('hire_car_time') if data.get('hire_car_time') else None,
                    'slot': data.get('slot'),
                }
            )

            return {'success': True, 'message': 'Location and time slot successfully booked.'}

        except Exception as e:
            return {'success': False, 'message': str(e)}