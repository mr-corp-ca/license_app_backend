from rest_framework import serializers
from .models import *


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