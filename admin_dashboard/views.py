import threading
import calendar
from admin_dashboard.serializers.user_serializer import AdminNewUserSerializer, AdminUserGetSerializer, DefaultAdminUserSerializer
from admin_dashboard.serializers.course_serializer import AdminGETCourseSerializer,SchoolApprovalSerializer,AdminDrivingSchoolListSerializer
from course_management_app.models import Course, UserSelectedCourses
from user_management_app.models import TransactionHistroy, User
from .models import *
from .serializers import *
from itertools import chain
from course_management_app.serializers import *
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
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
    queryset = User.objects.filter(Q(user_type='learner') | Q(user_type='instructor')).order_by('-date_joined')
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
        user_profile_courses, created = UserSelectedCourses.objects.get_or_create(
            user=user,
        )
        
        if user.user_type == 'learner':
            courses = user_profile_courses.courses.all()
            packages = Package.objects.filter(user=user)
            vehicles = Vehicle.objects.filter(user=user)

            # Serialize data
            user_data = {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "email": user.email,
                "address" : user.address,
                "phone_number": user.phone_number,
                "dob": user.dob,
                "user_type": user.user_type,
                "logo": user.logo.url if user.logo else None,
                "course": AdminGETCourseSerializer(courses, many=True).data,
                "packages": GETPackageSerializer(packages, many=True).data,
                "vehicles": VehicleSerializer(vehicles, many=True).data,
            }

            return Response(user_data)
        elif user.user_type == 'instructor':
            ids = Course.objects.filter(user=user).values_list('id',flat=True)
            total_learner = UserSelectedCourses.objects.filter(id__in=ids).count()
            packages = Package.objects.filter(user=user)
            total_lesson = Lesson.objects.filter(course__user=user).count()
            vehicles = Vehicle.objects.filter(user=user)
            course = Course.objects.filter(user=user)
            total_vehicle = vehicles.count()
            user_data = {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "address" :  user.address,
                "email": user.email,
                "phone_number": user.phone_number,
                "dob": user.dob,
                "user_type": user.user_type,
                "logo": user.logo.url if user.logo else None,
                "total_learner": total_learner,
                "total_lesson": total_lesson,
                "course" : GETCourseSerializer(course, many=True).data,
                "packages": GETPackageSerializer(packages, many=True).data,
                "total_vehicle" : total_vehicle,
                "vehicles": VehicleSerializer(vehicles, many=True).data,
            }
            return Response(user_data)
        else:
            return Response({'status':False,'message':'User type not found.'},status=status.HTTP_400_BAD_REQUEST)
        
 
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
            user = User.objects.get(id=id)
            
            if user_status:
                user.user_status = user_status
            user.save()
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