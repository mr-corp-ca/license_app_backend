import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from datetime import date
from course_management_app.models import Course, Vehicle
from timing_slot_app.constants import calculate_end_time, get_day_name, get_schedule_times, validate_even_or_odd,convert_time
from user_management_app.threads import send_push_notification
from utils_app.models import Location,Radius
from user_management_app.models import SchoolSetting, User, UserNotification, Wallet,TransactionHistroy
from datetime import datetime, timedelta, time
from utils_app.serializers import LocationSerializer
from .models import MonthlySchedule,LearnerBookingSchedule, SpecialLesson
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from .serializers import GETLearnerBookingScheduleSerializer, GETMonthlyScheduleSerializer, LearnerDataScheduleSerializer, MonthlyScheduleSerializer, SpecialLessonSerializer, UserLessonSerializer
from django.db.models import Min
from django.shortcuts import get_object_or_404
from django.db.models import Case, When, Value, IntegerField
from django.db.models import Count, Q, Min, F, ExpressionWrapper, FloatField, Max
from django.db.models.functions import Cast

class MonthlyScheduleAPIView(APIView):

    def post(self, request):
        serializer = MonthlyScheduleSerializer(data=request.data, many=True)
        if serializer.is_valid():
            results = []
            for item in serializer.validated_data:
                try:
                    result = self.process_schedule_item(item, request.user)
                    results.append(result)
                except ValueError as e:
                    return Response(
                        {
                            'success': False,
                            'message': str(e),
                            'date': item['date'].strftime('%Y-%m-%d')
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            return Response(
                {
                    "success": True,
                    "message": "Schedules optimized",
                    "results": results
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def process_schedule_item(self, item, user):
        """Process one schedule date"""
        date_str = item['date'].strftime('%Y-%m-%d')
        
        # 1. Calculate initial end_time based on operation_hour
        self.set_initial_end_time(item)
        
        # 2. Generate all possible time slots
        all_slots = self.generate_all_possible_slots(item)
        
        # 3. Calculate optimized lesson slots
        lesson_slots = self.calculate_lesson_slots(item, all_slots)
        
        # 4. Auto-place breaks at valid boundaries
        self.auto_place_breaks(item, lesson_slots)
        
        # 5. Save to database
        self.save_schedule(item, user)
        
        return {
            'date': date_str,
            'start_time': item['start_time'].strftime('%H:%M'),
            'end_time': item['end_time'].strftime('%H:%M'),
            'total_lessons': len([s for s in lesson_slots if s['type'] == 'lesson']),
            'total_gaps': len([s for s in lesson_slots if s['type'] == 'gap']),
            'slots': self.format_slots_for_response(lesson_slots)
        }

    def set_initial_end_time(self, item):
        """Set end_time based on start_time + operation_hour"""
        start_datetime = datetime.combine(item['date'], item['start_time'])
        end_datetime = start_datetime + timedelta(hours=item.get('operation_hour', 9))
        item['end_time'] = end_datetime.time()

    def generate_all_possible_slots(self, item):
        """Generate all possible time slots for the day"""
        slots = []
        current_time = item['start_time']
        end_time = item['end_time']
        
        while current_time < end_time:
            # Lesson slot (always 1 hour)
            lesson_end = (datetime.combine(item['date'], current_time) + 
                        timedelta(hours=1)).time()
            if lesson_end > end_time:
                break
            slots.append({
                'type': 'lesson',
                'start': current_time,
                'end': lesson_end,
                'duration': 60
            })
            current_time = lesson_end
            
            # Gap slot (flexible duration)
            gap_duration = min(
                item.get('lesson_gap', 30),  # Default 30 mins
                self.calculate_remaining_mins(current_time, end_time)
            )
            if gap_duration > 0:
                gap_end = (datetime.combine(item['date'], current_time) + 
                         timedelta(minutes=gap_duration)).time()
                slots.append({
                    'type': 'gap',
                    'start': current_time,
                    'end': gap_end,
                    'duration': gap_duration
                })
                current_time = gap_end
        
        return slots

    def calculate_lesson_slots(self, item, all_slots):
        """Select which slots will be used for lessons"""
        lesson_slots = []
        remaining_mins = self.calculate_total_available_mins(item)
        
        for slot in all_slots:
            if remaining_mins <= 0:
                break
                
            if slot['type'] == 'lesson':
                lesson_slots.append(slot)
                remaining_mins -= slot['duration']
            else:
                # Only include gap if there's another lesson after it
                next_lesson = next(
                    (s for s in all_slots if s['type'] == 'lesson' and s['start'] >= slot['end']),
                    None
                )
                if next_lesson:
                    lesson_slots.append(slot)
        
        # Adjust end_time if we have remaining minutes
        if remaining_mins > 0:
            last_slot = lesson_slots[-1]
            new_end = (datetime.combine(item['date'], last_slot['end']) + 
                      timedelta(minutes=remaining_mins)).time()
            item['end_time'] = new_end
            lesson_slots.append({
                'type': 'lesson',
                'start': last_slot['end'],
                'end': new_end,
                'duration': remaining_mins,
                'partial': True
            })
        
        return lesson_slots

    def auto_place_breaks(self, item, lesson_slots):
        """Automatically adjust breaks to fit lesson boundaries"""
        lesson_boundaries = [
            slot['start'] for slot in lesson_slots if slot['type'] == 'lesson'
        ] + [item['end_time']]
        
        if 'launch_break_start' in item:
            closest = self.find_closest_boundary(
                item['launch_break_start'], 
                lesson_boundaries
            )
            item['launch_break_start'] = closest
            item['launch_break_end'] = (datetime.combine(item['date'], closest) + 
                                      timedelta(hours=1)).time()
        
        if 'extra_space_start' in item:
            closest = self.find_closest_boundary(
                item['extra_space_start'], 
                lesson_boundaries
            )
            item['extra_space_start'] = closest
            item['extra_space_end'] = (datetime.combine(item['date'], closest) + 
                                     timedelta(minutes=30)).time()

    def find_closest_boundary(self, target_time, boundaries):
        """Find closest lesson boundary to requested time"""
        return min(
            boundaries,
            key=lambda x: abs(
                datetime.combine(datetime.today(), x) - 
                datetime.combine(datetime.today(), target_time)
            )
        )

    def calculate_remaining_mins(self, current_time, end_time):
        """Calculate remaining minutes between two times"""
        return int(
            (datetime.combine(datetime.today(), end_time) - 
            datetime.combine(datetime.today(), current_time)
        ).total_seconds() / 60)

    def calculate_total_available_mins(self, item):
        """Calculate total available minutes in the schedule"""
        return int(
            (datetime.combine(item['date'], item['end_time']) - 
             datetime.combine(item['date'], item['start_time'])
            ).total_seconds() / 60
        )

    def format_slots_for_response(self, slots):
        """Format time slots for API response"""
        return [
            {
                'type': slot['type'],
                'start': slot['start'].strftime('%H:%M'),
                'end': slot['end'].strftime('%H:%M'),
                'duration': slot.get('duration', 0),
                'partial': slot.get('partial', False)
            }
            for slot in slots
        ]
        
    def save_schedule(self, item, user):
        """Save optimized schedule to database"""
        item['user'] = user
        vehicle = item.get('vehicle_id') or Vehicle.objects.first()
        defaults = {
            'start_time': item['start_time'],
            'end_time': item['end_time'],
            'lesson_gap': item['lesson_gap'],
            'lesson_duration': item['lesson_duration'],
            'operation_hour': item.get('operation_hour'),
            'launch_break_start': item.get('launch_break_start'),
            'launch_break_end': item.get('launch_break_end'),
            'extra_space_start': item.get('extra_space_start'),
            'extra_space_end': item.get('extra_space_end'),
            'user': user
        }
        
        schedule, created = MonthlySchedule.objects.update_or_create(
            date=item['date'],
            vehicle=vehicle,
            user=user,
            defaults=defaults
        )
        return schedule
    
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


class AvailableBreakTimesAPIView(APIView):
    
    def get(self, request):
        # Get query parameters
        date = request.query_params.get('date')
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        lesson_duration = request.query_params.get('lesson_duration')
        lesson_gap = request.query_params.get('lesson_gap', 0)
        
        # Validate required parameters
        if not all([date, start_time, end_time, lesson_duration]):
            return Response(
                {'success': False, 'message': 'date, start_time, end_time, and lesson_duration are required parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Parse the input data
            parsed_date = datetime.strptime(date, '%Y-%m-%d').date()
            parsed_start_time = datetime.strptime(start_time, '%H:%M').time()
            parsed_end_time = datetime.strptime(end_time, '%H:%M').time()
            lesson_duration = float(lesson_duration)
            lesson_gap = int(lesson_gap)
            
            # Create a mock item similar to what we have in the POST request
            item = {
                'date': parsed_date,
                'start_time': parsed_start_time,
                'end_time': parsed_end_time,
                'lesson_duration': lesson_duration,
                'lesson_gap': lesson_gap,
            }
            
            # Calculate lesson slots
            lesson_slots = self.calculate_lesson_slots(item)
            
            # Get all valid break start times (lesson end times)
            valid_break_times = [slot['end'] for slot in lesson_slots if slot['type'] == 'lesson']
            
            # If no lessons, the whole schedule is available
            if not valid_break_times:
                available_slots = [{
                    'start': item['start_time'].strftime('%H:%M'),
                    'end': item['end_time'].strftime('%H:%M'),
                    'duration': (datetime.combine(datetime.today(), item['end_time']) - 
                                datetime.combine(datetime.today(), item['start_time'])).seconds / 3600
                }]
            else:
                available_slots = []
                
                # Check time before first lesson
                first_lesson_start = lesson_slots[0]['start']
                if item['start_time'] < first_lesson_start:
                    available_slots.append({
                        'start': item['start_time'].strftime('%H:%M'),
                        'end': first_lesson_start.strftime('%H:%M'),
                        'duration': (datetime.combine(datetime.today(), first_lesson_start) - 
                                    datetime.combine(datetime.today(), item['start_time'])).seconds / 3600
                    })
                
                # Check times between lessons
                for i in range(len(lesson_slots)-1):
                    current_end = lesson_slots[i]['end']
                    next_start = lesson_slots[i+1]['start']
                    if current_end < next_start:
                        available_slots.append({
                            'start': current_end.strftime('%H:%M'),
                            'end': next_start.strftime('%H:%M'),
                            'duration': (datetime.combine(datetime.today(), next_start) - 
                                        datetime.combine(datetime.today(), current_end)).seconds / 3600
                        })
                
                # Check time after last lesson
                last_lesson_end = lesson_slots[-1]['end']
                if last_lesson_end < item['end_time']:
                    available_slots.append({
                        'start': last_lesson_end.strftime('%H:%M'),
                        'end': item['end_time'].strftime('%H:%M'),
                        'duration': (datetime.combine(datetime.today(), item['end_time']) - 
                                    datetime.combine(datetime.today(), last_lesson_end)).seconds / 3600
                    })
            
            return Response({
                'success': True,
                'date': date,
                'available_break_times': available_slots,
                # 'lesson_slots': [{
                #     'start': slot['start'].strftime('%H:%M'),
                #     'end': slot['end'].strftime('%H:%M'),
                #     'type': slot['type']
                # } for slot in lesson_slots]
            })
            
        except ValueError as e:
            return Response(
                {'success': False, 'message': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def calculate_lesson_slots(self, item):
        """Calculate all possible lesson slots (same as in MonthlyScheduleAPIView)"""
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

                school_setting, created = SchoolSetting.objects.get_or_create(user=vehicle.user)
                school_setting.learner.add(user)

                course = Course.objects.filter(user=vehicle.user).first()
                return Response({
                    'success': True,
                    'available_slots': available_slots,
                    'locations': serialized_locations,
                    'hire_car_price': course.hire_car_price,

                    'current_location_option': {
                        'location_name': current_location_name,
                        'current_location_price': radius.current_location_price
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
                

            title = '📚 Lesson Booking Confirmed'
            message = '✅ Your lesson has been successfully booked or updated. 🕒'

            notification_type = 'general'
            send_push_notification(user, title, message, notification_type)
            UserNotification.objects.create(user=user, noti_type=notification_type, text=message, title=title)
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
        
        existing_lesson = SpecialLesson.objects.filter(user=user, vehicle=vehicle, hire_car_status='Pending').first()
        if existing_lesson:
            return Response(
                {'success': False, 'response':{'message': 'Please wait for approval. You have already applied to hire a car!'}},
                status=status.HTTP_400_BAD_REQUEST
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
        

            title = '📤 Hire a Car  Request Submitted 🚗'
            message = '⏳ Your hire a car request has been submitted to the instructor. Awaiting approval. 🚗'

            notification_type = 'general'
            send_push_notification(user, title, message, notification_type)
            UserNotification.objects.create(user=user, noti_type=notification_type, text=message, title=title)

            
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


class MyBookedVehicleApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_bookings = LearnerBookingSchedule.objects.filter(user=user).values('vehicle').annotate(min_date=Min('date')).values_list('id', flat=True)
        distinct_bookings = LearnerBookingSchedule.objects.filter(id__in=user_bookings)

        serializer = GETLearnerBookingScheduleSerializer(distinct_bookings, many=True)
        return Response({"success": True, "response": {"data": serializer.data}}, status=status.HTTP_200_OK)
    
class RequestSpecialLessonApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # lessons = SpecialLesson.objects.filter(vehicle__user=user)
        lessons = SpecialLesson.objects.filter(vehicle__user=user).annotate(
        status_order=Case(
            When(hire_car_status='Pending', then=Value(0)),
            When(hire_car_status='Rejected', then=Value(1)),
            When(hire_car_status='Accepted', then=Value(2)),
            default=Value(3),  # for null or blank values
            output_field=IntegerField(),
        )
    ).order_by('status_order')

        serializer = SpecialLessonSerializer(lessons, many=True)
        return Response({"success": True, "response": {"data": serializer.data}}, status=status.HTTP_200_OK)



class UpdateSpecialLessonStatusApiView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        user = request.user
        request_type = request.data.get('request_type')
        
        if request_type not in ['Accepted', 'Rejected']:
            return Response(
                {"success": False, "response": {"message": "Invalid request type. Must be 'Accepted' or 'Rejected'."}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the lesson and verify it belongs to the user
        lesson = get_object_or_404(SpecialLesson, id=id, vehicle__user=user)
        
        title = '🛑 Hire a Car Request Rejected'
        message = '❌ The instructor has rejected your hire a car request. ℹ️ For more details, please contact 🛠️ Help & Support.'

        # Update the status
        lesson.hire_car_status = request_type
        lesson.save()
        if request_type == 'Accepted':
            title = '🚗 Hire a Car Request Accepted'
            message = '✅ The instructor has accepted your hire a car request. 🚗 Get ready to go!'

            LearnerBookingSchedule.objects.update_or_create(
                user=lesson.user,
                vehicle=lesson.vehicle,
                special_lesson=True,
                defaults={
                    'date': lesson.hire_car_date,
                    'slot': lesson.hire_car_time
                }
            )
        

        notification_type = 'general'
        send_push_notification(user, title, message, notification_type)
        UserNotification.objects.create(user=user, noti_type=notification_type, text=message, title=title)


        serializer = SpecialLessonSerializer(lesson)
        return Response(
            {"success": True, "response": {"message": f"Request {request_type.lower()} successfully.", "data": serializer.data}},
            status=status.HTTP_200_OK
        )
    


class LessonDataApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = date.today()
        user = request.user
        
        if user.user_type not in ['school', 'learner']:
            return Response(
                {
                    'success': False,
                    'response': {
                        'message': 'You do not have permission to access this data.'
                    }
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Get the base queryset based on user type
        if user.user_type == 'school':
            # For school, get all learners associated with their vehicles
            learners = User.objects.filter(
                learnerweekly_user__vehicle__user=user,
                user_type='learner'
            ).distinct()
        elif user.user_type == 'learner':
            # For learner, just get themselves
            learners = User.objects.filter(id=user.id)
            
        # Annotate the learner data with lesson statistics
        learners = learners.annotate(
            total_lessons=Count('learnerweekly_user'),
            completed_lessons=Count(
                'learnerweekly_user',
                filter=Q(learnerweekly_user__date__lt=today)
            ),
            ongoing_lessons=Count(
                'learnerweekly_user',
                filter=Q(learnerweekly_user__date__gte=today)
            ),
            earliest_lesson_date=Min('learnerweekly_user__date'),
            latest_lesson_date=Max('learnerweekly_user__date'),
            completion_percentage=Case(
                When(total_lessons=0, then=0.0),
                default=ExpressionWrapper(
                    Cast(F('completed_lessons'), FloatField()) / 
                    Cast(F('total_lessons'), FloatField()) * 100,
                    output_field=FloatField()
                ),
                output_field=FloatField()
            )
        ).order_by('-ongoing_lessons', '-completed_lessons')

        # Get detailed lesson data for each learner
        ongoing_users = []
        completed_users = []
        
        for learner in learners:
            # Get all lessons for this learner
            lessons = LearnerBookingSchedule.objects.filter(user=learner)
            
            # Serialize the learner data
            learner_data = UserLessonSerializer(learner, context={'user': user}).data
            
            # Add lesson details
            learner_data['lessons'] = LearnerDataScheduleSerializer(lessons, many=True).data
             
            # Sort lessons by date
            learner_data['lessons'].sort(key=lambda x: x['date'])
            
            # Categorize the learner
            if learner.ongoing_lessons > 0:
                ongoing_users.append(learner_data)
            elif learner.completed_lessons > 0:
                completed_users.append(learner_data)
        
        return Response({
            'success': True,
            'response': {
                'ongoing_lessons_users': ongoing_users,
                'completed_lessons_users': completed_users,
                'stats': {
                    'total_learners': learners.count(),
                    'total_ongoing': len(ongoing_users),
                    'total_completed': len(completed_users),
                }
            }
        })
    
