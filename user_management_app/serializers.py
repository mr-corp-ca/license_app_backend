from rest_framework import serializers
from django.db.models import Avg
from course_management_app.models import Course, Vehicle,Package,Service,Lesson, LicenseCategory, LearnerSelectedPackage, SchoolRating
from timing_slot_app.models import LearnerBookingSchedule
from utils_app.serializers import CitySerializer, ProvinceSerializer
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'user_type', 'dob', 'license_number', 'full_name', 'city', 'province', 'logo']
    
class UserGETSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'user_type', 'dob', 'license_number', 'full_name',
                  'phone_number']

class DefaultUserSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'user_type', 'dob', 'license_number', 'full_name', 'logo',
                 'phone_number', 'province', 'city']

    def get_city(self, instance):
        if instance.city:
            return CitySerializer(instance.city).data
        else:
            return None
        
    def get_province(self, instance):
        if instance.province:
            return ProvinceSerializer(instance.province).data
        else:
            return None

class SchoolUserSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()
    school_profile = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'user_type', 'dob', 'license_number', 'full_name', 'logo',
                  'phone_number', 'province', 'city', 'school_profile']

    def get_city(self, instance):
        if instance.city:
            return CitySerializer(instance.city).data
        else:
            return None
        
    def get_province(self, instance):
        if instance.province:
            return ProvinceSerializer(instance.province).data
        else:
            return None
class LicenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseCategory
        fields = ['id', 'name']

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name']


class SchoolUserSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()
    school_profile = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'user_type', 'dob', 'license_number', 'full_name', 'logo',
                  'phone_number', 'province', 'city', 'school_profile']

    def get_city(self, instance):
        if instance.city:
            return CitySerializer(instance.city).data
        else:
            return None
        
    def get_province(self, instance):
        if instance.province:
            return ProvinceSerializer(instance.province).data
        else:
            return None
    
    def get_school_profile(self, instance):
        profile = SchoolProfile.objects.filter(user=instance).first()
        if profile:
            return SchoolProfileSerializer(profile).data
        else:
            return None
        
class DriverProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfile
        fields = ['user', 'user_logo', 'institude_name', 'description', 'institude_image', 
                  'trainer_name', 'license_no', 'address', 'total_lesson', 'price']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'rating', 'feedback']

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'user', 'balance']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistroy
        fields = ['id', 'wallet', 'amount', 'transaction_type']


class UserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotification
        fields = ['id', 'user', 'status', 'noti_type', 'description']   
        

class LearnerReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearnerReport
        fields = ['id', 'learner', 'instructor', 'reason', 'description']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course  
        fields = ['id', 'title', 'price', 'lesson_numbers']


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'name', 'vehicle_model']


class SchoolSerializer(serializers.ModelSerializer):
    courses = serializers.SerializerMethodField()
    vehicles = VehicleSerializer(many=True, source='user_vehicle.all')
    rating = serializers.SerializerMethodField()

    class Meta:
        model = User 
        fields = ['id', 'username', 'address', 'logo', 'courses', 'vehicles', 'rating']

    def get_courses(self, obj):
        courses = self.context.get('courses', obj.course_user.all())
        return CourseSerializer(courses, many=True).data

    def get_rating(self, obj):
        return obj.review_set.aggregate(avg_rating=Avg('rating')).get('avg_rating', None)

class GetLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id','title']

class GetServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name']
class GetCourseSerializer(serializers.ModelSerializer):
    services = GetServiceSerializer(many=True)
    lesson = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'price', 'lesson_numbers', 'services', 'refund_policy','lesson']
    
    def get_lesson(self, instance):
        lesson = Lesson.objects.filter(course=instance)
        return GetLessonSerializer(lesson, many=True).data

class GetVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'name', 'vehicle_model']

class GetReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name')

    class Meta:
        model = Review
        fields = ['id', 'user_name', 'rating','feedback']

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ['id', 'name', 'price','lesson_numbers','total_course_hour','free_pickup']

class SchoolDetailSerializer(serializers.ModelSerializer):
    courses = serializers.SerializerMethodField()
    vehicles = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    plans = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'address', 'logo', 'rating', 
            'courses', 'vehicles', 'reviews', 'plans'
        ]

    def get_courses(self, obj):
        courses = obj.course_user.all()
        return GetCourseSerializer(courses, many=True).data

    def get_vehicles(self, obj):
        vehicles = obj.user_vehicle.all()
        return GetVehicleSerializer(vehicles, many=True).data

    def get_reviews(self, obj):
        reviews = obj.review_set.all()
        return GetReviewSerializer(reviews, many=True).data

    def get_plans(self, obj):
        plans = obj.package_user.all() 
        return PlanSerializer(plans, many=True).data

    def get_rating(self, obj):
        return obj.review_set.aggregate(avg_rating=Avg('rating')).get('avg_rating', None)
    

class VehicleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'name', 'vehicle_registration_no', 'vehicle_model', 'image', 'booking_status','created_at']


class SchoolProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolProfile
        fields = ['user', 'institute_name', 'instructor_name', 'license_category', 'services', 'registration_file']


class LearnerSelectedPackageServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name']


class LearnerSelectedPackageSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField()
    lesson_number = serializers.SerializerMethodField()
    package_name = serializers.CharField(source='package.name', read_only=True)

    class Meta:
        model = LearnerSelectedPackage
        fields = ['id', 'package', 'package_name','services', 'lesson_number']

    def get_services(self, obj):
        return LearnerSelectedPackageServiceSerializer(obj.package.services.all(), many=True).data

    def get_lesson_number(self, obj):
        if obj.package:
            return obj.package.lesson_numbers
        else:
            return 0

class LearnerBookingScheduleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  LearnerBookingSchedule
        fields = ['id','road_test','road_test_date','road_test_time','special_lesson','hire_car','hire_car_date','hire_car_time']

class LearnerDetailSerializer(serializers.ModelSerializer):
    package = serializers.SerializerMethodField()
    booking_schedule = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id','user_type','full_name', 'email', 'dob', 'license_number', 'address', 'phone_number', 'package', 'booking_schedule']

    def get_package(self, obj):
        user = self.context.get('user')
        package = LearnerSelectedPackage.objects.filter(user=obj, package__user=user).first()
        return LearnerSelectedPackageSerializer(package).data if package else None
    
    def get_booking_schedule(self, obj):
        user = self.context.get('user')
        booking = LearnerBookingSchedule.objects.filter(user=obj, vehicle__user=user).first()
        return LearnerBookingScheduleSerializer(booking).data if booking else None

class SchoolRatingSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = ['id', 'logo', 'full_name', 'rating', 'feedback']
    def get_logo(self,obj):
       if obj.user.logo:
            logo = obj.user.logo
            return logo
       else:
            return None
    def get_full_name(self,obj):
        if obj.user.full_name:
            full_name = obj.user.full_name
            return full_name
        else:
            return None