from rest_framework import serializers
from django.db.models import Avg
from utils_app.models import City, Province
from user_management_app.models import *
from course_management_app.models import *
from timing_slot_app.models import *
from course_management_app.serializers import VehicleSerializer


class AdminCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']

class AdminProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['id', 'name']

class UserProfileSerializer(serializers.ModelSerializer):
    selected_package = serializers.SerializerMethodField()
    lesson_number = serializers.SerializerMethodField()
    institute_name = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    learner_rating = serializers.SerializerMethodField()

    vehicles = serializers.SerializerMethodField()
    feedback = serializers.SerializerMethodField()
    course_progress = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = [
            "id", "username", "full_name", "logo", "email", "address", "phone_number", "license_number", "dob", "user_type",
            "selected_package", "lesson_number", "institute_name", "average_rating", "learner_rating", "feedback", "course_progress", "vehicles"
        ]
    
    def get_selected_package(self, obj):
        learner_selected_package = LearnerSelectedPackage.objects.filter(user=obj).first()
        if learner_selected_package:
            return learner_selected_package.package.name
        return None

    def get_lesson_number(self, obj):
        user_courses, created = UserSelectedCourses.objects.get_or_create(user=obj)
        print("user_courses--------------->",user_courses)
        if user_courses:
            first_course = user_courses.courses.first()  
            print("first_course--------------->",first_course)
            if first_course:
                return first_course.lesson_numbers if first_course.lesson_numbers else 0
        return 0
    
    def get_institute_name(self, obj):
        school_setting = SchoolSetting.objects.filter(learner=obj).first()
        if school_setting:
            school_profile = SchoolProfile.objects.filter(user=school_setting.user).first()
            if school_profile:
                return school_profile.institute_name
            else:
                return None
        return None
    
    def get_learner_rating(self, obj):
        user_courses, created = UserSelectedCourses.objects.get_or_create(user=obj)
        if user_courses:
            first_course = user_courses.courses.first()  
            if first_course:
                rating = SchoolRating.objects.filter(user=obj, course=first_course).first()
                if rating:
                    return rating.rating
        return None
    
    def get_average_rating(self, obj):
        reviews = Review.objects.filter(user=obj)
        if reviews:
            return reviews.aggregate(Avg('rating'))['rating__avg']
        return None
    
    def get_vehicles(self, obj):
       
        school_setting = SchoolSetting.objects.filter(learner=obj).first()
        if school_setting:
            school_profile = SchoolProfile.objects.filter(user=school_setting.user).first()
            if school_profile:
                vehicles = Vehicle.objects.filter(user=school_profile.user)
                return VehicleSerializer(vehicles, many=True).data
        return [] 
  
    def get_course_progress(self, obj):
        user_courses, created = UserSelectedCourses.objects.get_or_create(user=obj)
        if user_courses:
            first_course = user_courses.courses.first()
            if first_course:
                learner_package = LearnerSelectedPackage.objects.filter(user=obj).first()
                if learner_package:
                    attended_lessons = learner_package.attended_lesson

                    total_lessons = first_course.lesson_numbers
                    if total_lessons > 0:
                        progress = (attended_lessons / total_lessons) * 100
                        return round(progress, 2)
        return 0
    
    def get_feedback(self, obj):
        reviews = Review.objects.filter(user=obj)
        if reviews:
            feedback = reviews.first().feedback
            return feedback if feedback else "No feedback provided"
        return "No feedback available"

    

    def to_representation(self, instance):
        """ Customize the serialization based on user type """
        data = super().to_representation(instance)
        
        if instance.user_type != 'learner':
            data.pop('selected_package', None)
            data.pop('lesson_number', None)
            data.pop('institute_name', None)
            data.pop('average_rating', None)
            data.pop('vehicles', None)
        
        return data