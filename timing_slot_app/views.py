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
from .models import MonthlySchedule,LearnerBookingSchedule, SpecialLesson
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

                    # Calculate all lesson time slots first
                    lesson_slots = self.calculate_lesson_slots(item)

                    # Get all valid break start times (lesson end times)
                    valid_break_times = [slot['end'] for slot in lesson_slots if slot['type'] == 'lesson']
                    
                    # If no lessons, break times must be None
                    if not valid_break_times:
                        if item.get('launch_break_start') or item.get('launch_break_end'):
                            raise ValueError(
                                f"On {date_str}: Cannot set break times when there are no lessons scheduled"
                            )
                        if item.get('extra_space_start') or item.get('extra_space_end'):
                            raise ValueError(
                                f"On {date_str}: Cannot set extra space times when there are no lessons scheduled"
                            )
                    else:
                        # Validate launch break times
                        if item.get('launch_break_start') or item.get('launch_break_end'):
                            if not (item.get('launch_break_start') and item.get('launch_break_end')):
                                raise ValueError(
                                    f"On {date_str}: Both launch break start and end times must be provided"
                                )
                            
                            if item['launch_break_start'] not in valid_break_times:
                                raise ValueError(
                                    f"On {date_str}: Launch break must start exactly when a lesson ends. "
                                    f"Valid start times: {', '.join([t.strftime('%H:%M') for t in valid_break_times])}"
                                )
                            
                            # Ensure break end is after start and within schedule
                            if item['launch_break_start'] >= item['launch_break_end']:
                                raise ValueError(
                                    f"On {date_str}: Launch break end time must be after start time"
                                )
                            
                            if item['launch_break_end'] > item['end_time']:
                                raise ValueError(
                                    f"On {date_str}: Launch break must end within scheduled hours "
                                    f"({item['end_time'].strftime('%H:%M')})"
                                )

                        # Validate extra space times
                        if item.get('extra_space_start') or item.get('extra_space_end'):
                            if not (item.get('extra_space_start') and item.get('extra_space_end')):
                                raise ValueError(
                                    f"On {date_str}: Both extra space start and end times must be provided"
                                )
                            
                            if item['extra_space_start'] not in valid_break_times:
                                raise ValueError(
                                    f"On {date_str}: Extra space must start exactly when a lesson ends. "
                                    f"Valid start times: {', '.join([t.strftime('%H:%M') for t in valid_break_times])}"
                                )
                            
                            # Ensure extra space end is after start and within schedule
                            if item['extra_space_start'] >= item['extra_space_end']:
                                raise ValueError(
                                    f"On {date_str}: Extra space end time must be after start time"
                                )
                            
                            if item['extra_space_end'] > item['end_time']:
                                raise ValueError(
                                    f"On {date_str}: The extra space end time falls within the lesson time. The suggested time is "
                                    f"({item['end_time'].strftime('%H:%M')})"
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
        """Calculate all possible lesson slots based on schedule, including gaps between lessons only"""
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
            
            # Add the lesson slot
            lesson_slots.append({
                'type': 'lesson',
                'start': current_time,
                'end': lesson_end,
                'formatted': f"{current_time.strftime('%H:%M')}-{lesson_end.strftime('%H:%M')}"
            })
            
            # Only add gap between lessons, not after breaks
            if lesson_gap > 0 and lesson_end < end_time:
                # Check if there's time for another lesson after the gap
                potential_next_lesson_start = (datetime.combine(datetime.today(), lesson_end) + 
                                            timedelta(minutes=lesson_gap)).time()
                
                potential_next_lesson_end = (datetime.combine(datetime.today(), potential_next_lesson_start) + 
                                        timedelta(hours=lesson_duration)).time()
                
                # Only add gap if there's room for another full lesson after it
                if potential_next_lesson_end <= end_time:
                    gap_end = potential_next_lesson_start
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
        - Break must start exactly when a lesson ends or at schedule start
        - Entire break period must not overlap with any lessons
        """
        # Get all valid break start times (lesson end times and schedule start)
        valid_start_times = []
        if lesson_slots:
            valid_start_times.append(lesson_slots[0]['start'])  # Schedule start time
            valid_start_times.extend([slot['end'] for slot in lesson_slots if slot['type'] == 'lesson'])
        
        # Check if break starts at a valid time
        starts_at_valid_time = any(break_start == start_time for start_time in valid_start_times)
        
        if not starts_at_valid_time:
            available_starts = sorted(list(set(t.strftime('%H:%M') for t in valid_start_times)))
            error = ValueError(
                f"On {date_str}: {break_name} must start when a lesson ends or at schedule start. "
                f"Available start times: {', '.join(available_starts)}"
            )
            error.available_times = available_starts
            raise error
        
        # Check if break overlaps with any lessons
        for slot in lesson_slots:
            if slot['type'] == 'lesson':  # Only check against lessons, not gaps
                if not (break_end <= slot['start'] or break_start >= slot['end']):
                    available_starts = sorted(list(set(t.strftime('%H:%M') for t in valid_start_times)))
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
        date = request.query_params.get('date')
        
        if not date:
            return Response(
                {'success': False, 'message': 'Date parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Validate date format
            datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get single schedule for the user and date
            schedule = MonthlySchedule.objects.get(
                user=request.user,
                date=date
            )
            serializer = GETMonthlyScheduleSerializer(schedule)
            
            return Response(
                {
                    'success': True,
                    'data': serializer.data,
                    'message': 'Schedule retrieved successfully'
                },
                status=status.HTTP_200_OK
            )
            
        except MonthlySchedule.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': 'No schedule found for this date',
                    'data': None
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
                
                print('**********', locations)

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

            vehicle_id = data.get('vehicle_id')
            if not vehicle_id:
                return Response(  # Changed from dict to Response
                    {'success': False, 'response': {'message': 'Please provide vehicle id in special lesson!'}},
                    status=status.HTTP_400_BAD_REQUEST
                )

            vehicle = Vehicle.objects.filter(id=vehicle_id).first()
            if not vehicle:
                return Response(  # Changed from dict to Response
                    {'success': False, 'message': 'Vehicle not found!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            SpecialLesson.objects.update_or_create(
                user=user,
                vehicle=vehicle,
                defaults={
                    'road_test': data.get('road_test', False),
                    'special_lesson': data.get('special_lesson', False),

                    # 'hire_car': data.get('hire_car', False),

                    'road_test_date': data.get('road_test_date') if data.get('road_test_date') else None,
                    'road_test_time': data.get('road_test_time') if data.get('road_test_time') else None,
                    'road_test_status': 'Pending'


                    # 'hire_car_date': data.get('hire_car_date') if data.get('hire_car_date') else None,
                    # 'hire_car_time': data.get('hire_car_time') if data.get('hire_car_time') else None,
                    # 'hire_car_price': data.get('hire_car_price') if data.get('hire_car_price') else None,

                    # 'hire_car_price_paid': bool(data.get('hire_car_price')),                
                    }
            )

            response_list = []
            for item in data.get('slot_data', []):
                response = self.process_booking(user, item)
                response_list.append(response)
                if not response.get('success'):
                    return Response(
                        {'success': False, 'response': response.get('message')},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            return Response({'success': True, 'response': response_list[0]}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'success': False, 'response': {'message': str(e)}},
                status=status.HTTP_400_BAD_REQUEST
            )
        

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

                    # 'road_test': data.get('road_test', False),
                    # 'hire_car': data.get('hire_car', False),
                    # 'road_test_date': data.get('road_test_date') if data.get('road_test_date') else None,
                    # 'road_test_time': data.get('road_test_time') if data.get('road_test_time') else None,
                    # 'hire_car_date': data.get('hire_car_date') if data.get('hire_car_date') else None,
                    # 'hire_car_time': data.get('hire_car_time') if data.get('hire_car_time') else None,

                    'slot': data.get('slot'),
                }
            )

            return {'success': True, 'message': 'Location and time slot successfully booked.'}

        except Exception as e:
            return {'success': False, 'message': str(e)}
        


class SpecialLessonRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        # Validate required fields
        vehicle_id = data.get('vehicle_id')
        if not vehicle_id:
            return Response(
                {'success': False, 'response':{'message': 'Vehicle ID is required.'}},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if vehicle exists
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            return Response(
                {'success': False, 'response':{'message': 'Vehicle not found.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        # Create or update special lesson
        try:
            special_lesson, created = SpecialLesson.objects.update_or_create(
                user=user,
                vehicle=vehicle,
                defaults={
                    'hire_car': True,
                    'hire_car_date': data.get('hire_car_date'),
                    'hire_car_time': data.get('hire_car_time'),
                    'hire_car_price': data.get('hire_car_price'),
                    'hire_car_status': 'Pending'
                }
            )
            
            return Response(
                {
                    'success': True, 
                    'response': {'message': 'Special lesson request submitted successfully.'},
                    'data': {
                        'id': special_lesson.id,
                        'status': 'Created' if created else 'Updated'
                    }
                },
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {'success': False, 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )