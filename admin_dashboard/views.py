import threading
from admin_dashboard.serializers.user_serializer import AdminNewUserSerializer, AdminUserGetSerializer, DefaultAdminUserSerializer
from course_management_app.models import Course
from user_management_app.models import TransactionHistroy, User
from .models import *
from .serializers import *
from itertools import chain
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
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime
from django.utils.timezone import now


def get_monthly_income(month=None):
    transactions = TransactionHistroy.objects.filter(
        created_at__year=datetime.now().year  # Filter for the current year
    ).annotate(month=TruncMonth('created_at'))  # Truncate date to month
    
    if month:
        transactions = transactions.filter(created_at__month=month)  # Filter by month if provided
    
    monthly_income = transactions.values('month').annotate(total_income=Sum('amount'))
    return monthly_income



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
        
        if month:
            try:
                month = int(month)
                if month < 1 or month > 12:
                    return Response({'success': False, 'message': 'Invalid month number'},
                                    status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({'success': False, 'message': 'Month must be an integer'},
                                status=status.HTTP_400_BAD_REQUEST)
        
        monthly_income = get_monthly_income(month)
        
        data = [
            {"month": income['month'].strftime('%B'), "total_income": income['total_income']}
            for income in monthly_income
        ]
        
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
    filterset_fields = ['user_type', 'is_active', 'is_deleted', 'email', 'phone_number', 'province__name', 'city__name']