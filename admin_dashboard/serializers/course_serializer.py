from rest_framework import serializers
from course_management_app.serializers import *
from course_management_app.models import Course,Lesson


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