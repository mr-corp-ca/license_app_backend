from rest_framework import serializers
from user_management_app.models import User
from course_management_app.serializers import *
from course_management_app.models import Course,Lesson,Vehicle,Package


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id','title']

class AdminCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields =[ 'user', 'title', 'description', 'price', 'lesson_numbers', 'refund_policy', 'course_cover_image']
class AdminGETCourseSerializer(serializers.ModelSerializer):
    lesson = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    license_category = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields =[ 'user', 'title', 'description', 'price', 'lesson_numbers', 'refund_policy', 'course_cover_image', 'services', 'license_category','lesson']
    
    def get_lesson(self, instance):
        lesson = Lesson.objects.filter(course=instance)
        return LessonSerializer(lesson, many=True).data

    def get_license_category(self, instance):
        license_category = instance.license_category.all()
        return LicenseCategorySerializer(license_category, many=True).data
    
    def get_services(self, instance):
        service_objects = instance.services.all()
        return ServiceSerializer(service_objects, many=True).data
    
    def get_lesson_count(self, instance):
        return Lesson.objects.filter(course=instance).count()

class SchoolLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'image']

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['name', 'vehicle_model', 'vehicle_registration_no', 'booking_status', 'image']

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ['name', 'price', 'total_course_hour', 'lesson_numbers', 'free_pickup']

class GETSchoolCourseSerializer(serializers.ModelSerializer):
    lesson = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    license_category = serializers.SerializerMethodField()
    total_instructors = serializers.SerializerMethodField()
    total_lessons = serializers.SerializerMethodField()
    plans = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'title','lesson_numbers',
            'course_cover_image', 'services',
            'license_category', 'lesson', 'total_instructors', 'total_lessons', 'plans'
        ]

    def get_lesson(self, instance):
        lesson = Lesson.objects.filter(course=instance)
        return SchoolLessonSerializer(lesson, many=True).data

    def get_license_category(self, instance):
        license_category = instance.license_category.all()
        return LicenseCategorySerializer(license_category, many=True).data

    def get_services(self, instance):
        service_objects = instance.services.all()
        return ServiceSerializer(service_objects, many=True).data

    def get_total_instructors(self, instance):
        school_setting = SchoolSetting.objects.filter(user=instance.user).first()
        if school_setting:
            return school_setting.instructor.count()
        return 0
    
        
    def get_total_lessons(self, instance):
        return Lesson.objects.filter(course=instance).count()

    def get_plans(self, instance):
        plans = Package.objects.filter(user=instance.user)
        return PackageSerializer(plans, many=True).data

class SchoolApprovalSerializer(serializers.ModelSerializer):
    courses = GETSchoolCourseSerializer(source= 'course_user',many=True)
    vehicles = VehicleSerializer(source='user_vehicle',many=True)
    packages = PackageSerializer(source = 'package_user',many=True)
    total_vehicle = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'email', 'address', 'logo', 'user_status',
            'courses','total_vehicle' ,'vehicles', 'packages'
        ]

    def get_vehicle(self,instance):
        vehicle = Vehicle.objects.filter(user=instance.user)
        return VehicleSerializer(vehicle, many=True).data
    
    def get_total_vehicle(self, instance):
        vehicle = Vehicle.objects.filter(user=instance)
        if vehicle:
            return vehicle.count()
        return 0
    