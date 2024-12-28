from rest_framework import serializers
from .models import *
from driving_license import settings
from user_management_app.models import*
class DiscountOfferUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id',  'user_type', 'full_name','logo']

class LicenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseCategory
        fields =['id', 'name']

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields =['id', 'name']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields =[ 'user', 'title', 'description', 'price', 'lesson_numbers', 'refund_policy', 'course_cover_image']


class GETCourseSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField()
    license_category = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields =[ 'id', 'user', 'title', 'description', 'price', 'lesson_numbers', 'refund_policy', 'course_cover_image', 'services', 'license_category']
    
    def get_license_category(self, instance):
        license_category = instance.license_category.all()
        return LicenseCategorySerializer(license_category, many=True).data
    
    def get_services(self, instance):
        service_objects = instance.services.all()
        return ServiceSerializer(service_objects, many=True).data

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ['id', 'user', 'name', 'price', 'total_course_hour', 'lesson_numbers', 'free_pickup']

class GETPackageSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField()
    class Meta:
        model = Package
        fields = ['id', 'user', 'name', 'price', 'total_course_hour', 'lesson_numbers', 'free_pickup', 'services']
    
    def get_services(self, instance):
        return ServiceSerializer(instance.services.all(), many=True).data
    
class DiscountOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountOffer
        fields = ['offer_type', 'name', 'audience', 'user', 'course', 'discount', 'start_date', 'end_date']

class GETDiscountOfferSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = DiscountOffer
        fields = ['offer_type', 'name', 'audience', 'user', 'course', 'discount', 'start_date', 'end_date']

    def get_user(self, instance):
        return DiscountOfferUserSerializer(instance.user).data

class CertificateSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = ['id', 'name', 'date', 'about', 'signature', 'logo', 'email', 'created_by', 'image']

    def get_logo(self, instance):
        if instance.logo:
            domain = getattr(settings, 'DOMAIN', '')
            return f"{domain}{instance.logo.url}"
        return None

    def get_image(self, instance):
        if instance.image:
            domain = getattr(settings, 'DOMAIN', '')
            return f"{domain}{instance.image.url}"
    

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['user', 'name', 'vehicle_registration_no', 'license_number', 'vehicle_model', 'image','booking_status']

class LearnerSelectedPackageSerializer(serializers.ModelSerializer):
    learner_selected_package = serializers.SerializerMethodField()
    course_lesson_numbers = serializers.SerializerMethodField()
    package_price = serializers.SerializerMethodField()
    lesson_completion_percentage = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'logo', 'learner_selected_package', 'course_lesson_numbers', 'package_price', 'lesson_completion_percentage']

    def get_logo(self, instance):
        return instance.logo.url if instance.logo else None

    def get_learner_selected_package(self, instance):
        learner_package = instance.learner_user.first()
        return learner_package.learner_selected_package if learner_package else 0

    def get_course_lesson_numbers(self, instance):
        return instance.course_user.first().lesson_numbers if instance.course_user.exists() else 0

    def get_package_price(self, instance):
        learner_package = instance.learner_user.first()
        return learner_package.package.price if learner_package else 0.0

    def get_lesson_completion_percentage(self, instance):
        learner_package = instance.learner_user.first()
        course = instance.course_user.first()
        return (learner_package.learner_selected_package / course.lesson_numbers) * 100 if learner_package and course else 0


