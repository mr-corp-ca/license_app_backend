from rest_framework import serializers
from django.db.models import Avg
from course_management_app.models import Course, Vehicle, Package, Service, Lesson, LearnerSelectedPackage, LearnerSelectedPackage, SchoolRating

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
        fields = ['id','title','image']

class GetServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name']
class GetCourseSerializer(serializers.ModelSerializer):
    lesson = serializers.SerializerMethodField()
    service = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = ['id', 'description','refund_policy','lesson','price','service']
    
    def get_lesson(self, instance):
        lessons = instance.lesson.all()  
        return GetLessonSerializer(lessons, many=True).data

    def get_service(self, instance):
        services = instance.service.all() 
        return GetServiceSerializer(services, many=True).data

class GetSchoolRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolRating
        fields = ['id','rating']

class GetReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username')
    user_piture = serializers.SerializerMethodField()
    # rating = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = ['id','user_name', 'user_piture','rating','feedback']
    
    def get_user_piture(self, obj):
        if obj.user and obj.user.logo:  # Check if user and logo exist
            return obj.user.logo.url  # Return the URL of the logo
        return None
    # def get_rating(self, obj):
    #     reviews = Review.objects.filter(user=obj.user)  
    #     avg_review_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
    #     return avg_review_rating
    
class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ['id', 'name', 'price','lesson_numbers','total_course_hour','free_pickup']

class SchoolDetailSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField()
    license_category = serializers.SerializerMethodField()
    # reviews = serializers.SerializerMethodField()
    plans = serializers.SerializerMethodField()
    # review_count = serializers.SerializerMethodField()
    school_rating = serializers.SerializerMethodField() 
    class Meta:
        model = SchoolProfile
        fields = [
            'institute_name', 'school_rating', 'course', 'license_category',
            'plans',
        ]
    
    def get_license_category(self, obj):
        categories = obj.license_category.all()
        return [{'id': category.id, 'name': category.name} for category in categories]

    
    def get_course(self, obj):
        course = Course.objects.filter(user=obj.user).first()
        return GetCourseSerializer(course).data

    def get_reviews(self, obj):
        reviews = Review.objects.filter(user=obj.user)
        
        if reviews:
            return GetReviewSerializer(reviews, many=True).data
        else:
            return None
    
    # def get_review_count(self,obj):
    #     review_count = Review.objects.filter(user=obj.user).count()
    #     return review_count
    
    def get_plans(self, obj):
        plans = Package.objects.filter(user=obj.user) 
        return PlanSerializer(plans, many=True).data

    def get_school_rating(self, obj):
        school_ratings = SchoolRating.objects.filter(course__user=obj.user)
        
        avg_rating = school_ratings.aggregate(avg_rating=Avg('rating'))['avg_rating']
        avg_rating = round(avg_rating, 1) if avg_rating is not None else None

        first_review = Review.objects.filter(user=obj.user).first()
        
        first_review_data = GetReviewSerializer(first_review).data if first_review else None
        
        school_reviews_count = Review.objects.filter(user=obj.user).count()
        
        return {
            'school_avg_rating': avg_rating,
            'review': first_review_data,
            'reviews_count': school_reviews_count
        }


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