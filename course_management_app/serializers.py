from rest_framework import serializers
from .models import *

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
        fields =[ 'user', 'title', 'description', 'price', 'lesson_numbers', 'refund_policy', 'course_cover_image', 'services', 'license_category']
    
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