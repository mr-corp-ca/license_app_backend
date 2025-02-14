from admin_dashboard.serializers.user_serializer import AdminNewUserSerializer, AdminUserGetSerializer, DefaultAdminUserSerializer, LearnerReportSerializer
from admin_dashboard.serializers.course_serializer import AdminDrivingSchoolListSerializer
from course_management_app.models import Course
from user_management_app.models import TransactionHistroy, User
from user_management_app.threads import send_push_notification
from .models import *

from django.db.models import Avg
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import *
from admin_dashboard.serializers.course_serializer import AdminCourseSerializer
from admin_dashboard.serializers.utils_serializer import UserProfileSerializer
from admin_dashboard.serializers.user_serializer import SchoolApprovalSerializer
from itertools import chain
from course_management_app.serializers import *
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.conf import settings
from rest_framework.generics import ListAPIView
from admin_dashboard.pagination import StandardResultSetPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Sum,Count,Case, When, Value, IntegerField
from django.db.models.functions import TruncMonth
from datetime import datetime
from django.utils.timezone import now
from django.shortcuts import render
from django.db.models import Q
from fcm_django.models import FCMDevice
from django.views.decorators.csrf import csrf_exempt

def get_monthly_income(data_type, month=None):
    try:

        if data_type == 'total_income':
            transactions = TransactionHistroy.objects.filter(
                created_at__year=datetime.now().year  # Filter for the current year
            ).annotate(month=TruncMonth('created_at'))  # Truncate date to month
            
            if month:
                transactions = transactions.filter(created_at__month=month)  # Filter by month if provided
            
            monthly_income = transactions.values('month').annotate(total_income=Sum('amount'))
            
            return monthly_income
        
        elif data_type == 'total_users':
            users = User.objects.filter(
                date_joined__year=datetime.now().year,
                user_type__in=['learner', 'instructor']
            ).annotate(month=TruncMonth('date_joined'))  # Truncate date to month

            if month:
                users = users.filter(date_joined__month=month)  # Filter by month if provided
            monthly_users = users.values('month').annotate(
                total_users=Count('id'),
                total_learners=Count('id', filter=Q(user_type='learner')),
                total_instructors=Count('id', filter=Q(user_type='instructor'))
            )
            return monthly_users
        elif data_type == 'total_schools':
            users = User.objects.filter(
                date_joined__year=datetime.now().year,
                user_type = 'instructor'
            ).annotate(month=TruncMonth('date_joined'))
            if month:
                users =  users.filter(date_joined__month=month)
            monthly_schools = users.values('month').annotate(Count('id'))
            return monthly_schools

        elif data_type == 'total_courses':
            courses = Course.objects.all().annotate(month=TruncMonth('created_at'))  

            if month:
                courses = courses.filter(created_at__month=month) 
            courses_data = courses.values('month').annotate(total_courses=Count('id'))
            
            return courses_data
        else:
            return Response({'success': False, 'message': 'Invalid data type provided'},
            status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({'status':False, 'message' : f"An unexpected error occurred : {str(e)}"},status=status.HTTP_400_BAD_REQUEST)


class AdminLoginApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        email = request.data.get('email').lower().strip() if 'email' in data else None
        password = data['password'] if 'password' in data else None

        if not email:
            return Response({"success": False, 'response': {'message': 'Email is required!'}},
                        status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response({"success": False, 'response': {'message': 'Password is required!'}},
                        status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"success": False, 'response': {'message': 'Incorrect Email'}},
                    status=status.HTTP_404_NOT_FOUND)
        
        if not user.is_active:
            return Response({"success": False, 'response': {'message': 'User is deleted or not active!'}},
                        status=status.HTTP_400_BAD_REQUEST)
        
        if not user.is_admin or not user.is_superuser:
            return Response({"success": False, 'response': {'message': 'You do not have access to this dashboard!'}},
                        status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=user, password=password)
        if not user:
            return Response({"success": False, 'response': {'message': 'Incorrect User Credentials!'}},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            token = Token.objects.get(user=user)
        except Token.DoesNotExist:
            token = Token.objects.create(user=user)
        access_token = token.key

        profile_obj = DefaultAdminUserSerializer(user).data
        return Response({'success': True, 'response': {'profile': profile_obj, 'access_token': access_token}},
                        status=status.HTTP_200_OK)


class AdminLogoutApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()

        return Response({'success': True, 'response': {'message': 'User Logged Out Successfully'}},
                        status=status.HTTP_200_OK)

class AdminDashboardApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data_dict = dict()
        today = now().date()

        total_user = User.objects.filter(Q(user_type='learner') | Q(user_type='instructor')).count()
        total_course = Course.objects.all().count()
        total_earning = 500
        total_school = 250

        new_user = User.objects.filter(Q(user_type='learner') | Q(user_type='instructor'), date_joined__date=today).order_by('-date_joined')

        data_dict['total_user'] = total_user
        data_dict['total_course'] = total_course
        data_dict['total_earning'] = total_earning
        data_dict['total_school'] = total_school
        data_dict['new_user'] = AdminNewUserSerializer(new_user, many=True).data
        return Response({'success': True, 'response': {'data': data_dict}},
                        status=status.HTTP_200_OK)


class AdminIncomeGraphAPIView(APIView):
    def get(self, request):
        month = request.GET.get('month', None)
        data_type = request.GET.get('data_type', None)

        if not data_type:
            return Response({'success': False, 'message': 'Invalid data type'},
                status=status.HTTP_400_BAD_REQUEST)
        
        if month:
            try:
                month = int(month)
                if month < 1 or month > 12:
                    return Response({'success': False, 'message': 'Invalid month number'},
                                    status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({'success': False, 'message': 'Month must be an integer'},
                                status=status.HTTP_400_BAD_REQUEST)
        
        monthly_data = get_monthly_income(data_type, month)
        if data_type == 'total_income':
            data = [
                {"month": month_data['month'].strftime('%B'), "total_income": month_data['total_income']}
                for month_data in monthly_data
            ]
        elif data_type == 'total_users':
            data = [
                {"month": month_data['month'].strftime('%B'), 
                 "total_users": month_data['total_users'],
                "total_learners": month_data['total_learners'],
                "total_instructors": month_data['total_instructors'],}
                for month_data in monthly_data
            ]
        elif data_type == 'total_schools':
            data = [
                {"month": month_data['month'].strftime('%B'),"total_instructors": month_data.get('id__count', 0) }
                for month_data in monthly_data
            ]
        elif data_type == 'total_courses':
            data = [
                {"month": month_data['month'].strftime('%B'),"total_courses":month_data['total_courses']}
                for month_data in monthly_data
            ]

        else:
            return Response({'success': False, 'message': 'Invalid data type provided'},
            status=status.HTTP_404_NOT_FOUND)

        return Response({'success': True, 'response': {'data': data}},
                        status=status.HTTP_200_OK)
    
            
class AdminUserListView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.filter(Q(user_type='learner') | Q(user_type='school')).order_by('-date_joined')
    serializer_class = AdminUserGetSerializer
    pagination_class = StandardResultSetPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['full_name']
    filterset_fields = ['user_type', 'is_active', 'is_deleted', 'email', 'phone_number', 'province', 'city']


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        
        user = User.objects.filter(id=id).first()
        if not user:
            return Response({'status':False,'message':'User not found.'},status=status.HTTP_404_NOT_FOUND)
        if user.user_type == 'learner':
            serializer = UserProfileSerializer(user)
            return Response({"success": True, "response": {"data": serializer.data}}, status=status.HTTP_200_OK)
        
        elif user.user_type == 'school':
                course = Course.objects.filter(user=user).first()

                school_setting = SchoolSetting.objects.filter(user=user).first()
                learners = school_setting.learner.all() if school_setting else []
                total_learner = len(learners)

                total_lessons = course.lesson_numbers if course else 0

                # Fetch other details
                packages = Package.objects.filter(user=user)
                vehicles = Vehicle.objects.filter(user=user)
                total_vehicle = vehicles.count()
                school_profile = SchoolProfile.objects.filter(user=user).first()
                license_categories = (
                        school_profile.license_category.values_list('name', flat=True) if school_profile else []
                    )
                payment_methods = (
                    TransactionHistroy.objects.filter(school=user)
                    .values_list('payment_method', flat=True)
                    .distinct())
                payment_methods_display = ', '.join(payment_methods) if payment_methods else "N/A"
                course_rating = Review.objects.filter(user=user).aggregate(Avg('rating'))['rating__avg']
                course_rating = round(course_rating, 1) if course_rating else 0

                user_data = {
                    "id": user.id,
                    "Institute_name": school_profile.institute_name,
                    "license_category": license_categories,
                    "full_name" :  school_profile.instructor_name,
                    "address": user.address,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "city" : user.city.name if user.city else None,
                    "user_type": user.user_type,
                    "logo": user.logo.url if user.logo else None,
                    "total_learner": total_learner,
                    "total_lesson": total_lessons,
                    "course": AdminCourseSerializer(course).data if course else None,
                    "packages": GETPackageSerializer(packages, many=True).data,
                    "total_vehicle": total_vehicle,
                    "vehicles": VehicleSerializer(vehicles, many=True).data,
                    "payment_methods": payment_methods_display,
                    "course_rating": course_rating,  
                }
                return Response({'success': True,'response': {'data':user_data}},status=status.HTTP_200_OK)
        else:
            return Response({'status':False,'resonse' : {'message':'User type not found.'}},status=status.HTTP_400_BAD_REQUEST)
        
 
class UserInactiveApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            user = User.objects.filter(id=id).first()

            if not user:
                return Response({'status': False, 'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            if user.is_active:
                user.is_active = False
                user.save()

                Token.objects.filter(user=user).delete()

                return Response({'status': True, 'message': 'User inactive successfully. Token deleted.'},status=status.HTTP_200_OK)
            else:
                user.is_active = True
                user.save()

                # token, created = Token.objects.get_or_create(user=user)
                return Response({'status': True,'message': 'User active successfully.'},status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': False, 'message': 'An error occurred.', 'error': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)


class AdminDeleteUserApiView(APIView):
    def delete(self, request, id):
        try:
            user = User.objects.filter(id=id).first()

            if not user:
                return Response({'status': False, 'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            if user.is_deleted:
                return Response({'status': False, 'message': 'User is already deleted.','is_deleted': user.is_deleted}, status=status.HTTP_404_NOT_FOUND)

            user.is_deleted = True
            user.is_active = False  
            user.save()

            Token.objects.filter(user=user).delete()

            return Response({'status': True, 'message': 'User account deleted successfully.','is_deleted': user.is_deleted}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': False, 'message': 'An error occurred.', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DrivingSchoolListAPIView(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.filter(user_type='school').order_by('-date_joined')
    serializer_class = AdminDrivingSchoolListSerializer
    pagination_class = StandardResultSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['full_name']
    filterset_fields = ['user_status']


class DrivingSchoolAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
            user_status = request.data.get('user_status')
            user = User.objects.filter(id=id).first()
            if not user:
                return Response({'success':False, 'response':{'message': 'user not found!'}}, status=status.HTTP_404_NOT_FOUND)

            
            if user_status:
                user.user_status = user_status
            user.save()

            # Sending notifications
            if user_status in ['accepted', 'rejected']:
                if user_status == 'accepted':
                    title = 'Enrollment Approved!'
                    message = "Congratulations! Your enrollment has been successfully approved by the Driving License School App. Welcome aboard!"
                elif user_status == 'rejected':
                    title = 'Enrollment Rejected'
                    message = "We regret to inform you that your enrollment has been rejected. Please contact support for further assistance."

                noti_type='general'
                send_push_notification(user, title, message, noti_type)
                UserNotification.objects.create(user=user, description=message, status=user_status, noti_type=noti_type)
            return Response({"message": "Status Updated successfully!"}, status=status.HTTP_200_OK)


class InstituteApprovaldetailApiView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request,id):
        try:
            user = User.objects.filter(id=id).first()
            if not user:
                return Response({'status': False, 'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = SchoolApprovalSerializer(user)
            return Response(
                {'status': True, 'data': serializer.data},
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {'status': False, 'message': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LessonListAPIView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = AdminLessonSerializer
    pagination_class = StandardResultSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()

        is_deleted = self.request.query_params.get('is_deleted', None)

        if is_deleted == 'true':
            queryset = queryset.filter(is_deleted=True)
        elif is_deleted == 'false':
            queryset = queryset.filter(is_deleted=False)  
        return queryset


class AdminAddLessonAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AdminLessonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'response': {'data': serializer.data}}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminUpdateLesson(APIView):
    permission_classes = []
    def put(self, request, id):
        try:
            lesson = Lesson.objects.get(id=id)
        except Lesson.DoesNotExist:
            return Response({'status': False, 'message': 'Lesson not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminLessonSerializer(lesson, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'response': {'data': serializer.data}}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminDeleteLesson(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, id):
        try:
            lesson = Lesson.objects.get(id=id)
        except Lesson.DoesNotExist:
            return Response({'status': False, 'message': 'Lesson not found.'}, status=status.HTTP_404_NOT_FOUND)

        lesson.is_deleted = True
        lesson.save()
        return Response({"message": "Lesson deleted successfully."}, status=status.HTTP_200_OK)


class AdminDashboardReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        report_type = request.query_params.get("type")

        if report_type == "learner":
            reports = LearnerReport.objects.filter(reported_by="learner")
        elif report_type == "school":
            reports = LearnerReport.objects.filter(reported_by="school")
        else:
            reports = LearnerReport.objects.all()

        serializer = LearnerReportSerializer(reports, many=True)

        return Response(
            {"success": True, "message": "Reports fetched successfully.", "data": serializer.data},
            status=status.HTTP_200_OK
        )


@csrf_exempt
def delete_user_account(request):
    context = {}

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        reason = request.POST.get('reason')

        user = User.objects.filter(Q(phone_number=phone_number) | Q(email=phone_number), is_deleted=False).first()

        if not user:
            context['user_message'] = 'The user with the provided email or phone number does not exist, or the account has been deleted.'
            context['color'] = 'danger'
            return render(request, 'license_app/accounts/delete_account.html', context)

        user.is_deleted = True
        
        user.deletd_reason = reason
        
        user.save()

        FCMDevice.objects.filter(user=user).delete()
        token = Token.objects.filter(user=user)
        if token:
            token.delete()

        context['user_message'] = 'The account has been deleted successfully!'
        context['color'] = 'success'

    return render(request, 'license_app/accounts/delete_account.html', context)
