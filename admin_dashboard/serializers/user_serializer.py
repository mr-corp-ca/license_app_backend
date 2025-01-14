from admin_dashboard.serializers.utils_serializer import AdminCitySerializer, AdminProvinceSerializer
from rest_framework import serializers
from django.db.models import Avg
from user_management_app.models import User, SchoolProfile, SchoolSetting,TransactionHistroy
from course_management_app.models import Course, Package, Vehicle,LicenseCategory, Lesson, Service
from utils_app.models import *

class DefaultAdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'phone_number', 'email', 'user_type', 'logo', 'dob', 'username']


class AdminNewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'username', 'email', 'user_type', 'logo']

class AdminCoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title']

class AdminUserGetSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()
    occupation = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    license_category = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'full_name', 'phone_number','is_active','is_deleted','username', 'email', 'address','user_type', 'logo', 'dob', 'date_joined', 'license_category', 'city', 'province', 'occupation','course']

    def get_city(self, instance):
        if instance.city:
            return AdminCitySerializer(instance.city).data
        else:
            return None

    def get_province(self, instance):
        if instance.province:
            return AdminProvinceSerializer(instance.province).data
        else:
            return None
        
    def get_occupation(self, instance):
        return 'Soft Engineer'
    
    def get_course(self,instance):
        course = Course.objects.filter(user=instance)
        if course:
            return AdminCoursesSerializer(course, many=True).data
        else:
            return None
    
    def get_license_category(self, instance):
        school_profile = SchoolProfile.objects.filter(user=instance).first()
        if school_profile and school_profile.license_category:
            return list(school_profile.license_category.values_list('name', flat=True))
        return []

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id','title','image']        

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City  
        fields = ['id', 'name']

class LicenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseCategory 
        fields = [ 'id','name'] 
class SchoolProfileSerializer(serializers.ModelSerializer):
    license_category = LicenseCategorySerializer(many=True)

    class Meta:
        model = SchoolProfile
        fields = ['institute_name','registration_file','license_category']

class AdminCourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(source='lesson', many=True)  
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'lesson_numbers','lessons','lesson_count']  
    
    def get_lesson_count(self, obj):
        return obj.lesson.count()

class ServiceSerializer(serializers.ModelSerializer):
    class Meta :
        model = Service
        fields =  ['name']

class PackageSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only = True)
    class Meta:
        model = Package
        fields = ['id', 'name', 'price','total_course_hour','lesson_numbers','free_pickup','services']

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'name', 'image', 'vehicle_registration_no'] 

class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistroy
        fields = ['payment_method']

class SchoolApprovalSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()
    school_profile = serializers.SerializerMethodField()
    total_learner = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    packages = serializers.SerializerMethodField()
    total_vehicle = serializers.SerializerMethodField()
    vehicles = VehicleSerializer(source='user_vehicle', many=True, read_only=True)
    payment_methods = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id','full_name', 'logo', 'school_profile', 'email','dob','phone_number', 'address', 'city', 'province', 
            'user_type', 'total_learner', 'course','packages',  'vehicles', 'total_vehicle', 'payment_methods'
        ]

    def get_school_profile(self, obj):
        school_profile = SchoolProfile.objects.filter(user=obj).first()
        return SchoolProfileSerializer(school_profile).data if school_profile else None

    def get_total_learner(self, obj):
        school_setting = SchoolSetting.objects.filter(user=obj).first()
        learners = school_setting.learner.all() if school_setting else []
        return len(learners)

    def get_course(self, obj):
        course = Course.objects.filter(user=obj).first()
        return AdminCourseSerializer(course).data if course else None

    def get_packages(self, obj):
        packages = Package.objects.filter(user=obj)
        return PackageSerializer(packages, many=True).data

    def get_total_vehicle(self, obj):
        vehicles = Vehicle.objects.filter(user=obj)
        return vehicles.count()

    def get_payment_methods(self, obj):
        payment_methods = (
            TransactionHistroy.objects.filter(school=obj)
            .values_list('payment_method', flat=True)
            .distinct()
        )
        return ', '.join(payment_methods) if payment_methods else "N/A"

    def get_city(self, instance):
        if instance.city:
            return AdminCitySerializer(instance.city).data
        else:
            return None

    def get_province(self, instance):
        if instance.province:
            return AdminProvinceSerializer(instance.province).data
        else:
            return None
