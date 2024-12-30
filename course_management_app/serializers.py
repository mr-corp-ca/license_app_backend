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
        fields =[ 'user', 'description', 'price', 'lesson_numbers', 'refund_policy', 'course_cover_image']


class GETCourseSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField()
    license_category = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields =[ 'id', 'user','description', 'price', 'lesson_numbers', 'refund_policy', 'course_cover_image', 'services', 'license_category']
    
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
        fields = ['id', 'offer_type', 'name', 'audience', 'user', 'course', 'discount', 'start_date', 'end_date']

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
    attended_lesson = serializers.SerializerMethodField()
    course_lesson_numbers = serializers.SerializerMethodField()
    package_price = serializers.SerializerMethodField()
    lesson_completion_percentage = serializers.SerializerMethodField()
    course_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'logo', 'attended_lesson', 'course_lesson_numbers', 'package_price', 'lesson_completion_percentage', 'courese_status']

    def get_logo(self, instance):
        return instance.logo.url if instance.logo else None

    def get_attended_lesson(self, instance):
        learner_package = instance.learner_user.first()
        return learner_package.attended_lesson if learner_package else 0

    def get_course_lesson_numbers(self, instance):
        return instance.course_user.first().lesson_numbers if instance.course_user.exists() else 0

    def get_package_price(self, instance):
        learner_package = instance.learner_user.first()
        return learner_package.package.price if learner_package else 0.0

    def get_lesson_completion_percentage(self, instance):
        learner_package = instance.learner_user.first()
        course = instance.course_user.first()
        return (learner_package.attended_lesson / course.lesson_numbers) * 100 if learner_package and course else 0

    def get_course_status(self, instance):
        learner_package = instance.learner_user.first()
        return learner_package.courese_status

 
class LessonRatingSerializer(serializers.ModelSerializer):
    learner = serializers.CharField(source="user.full_name", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)
    lesson = serializers.SerializerMethodField()  

    class Meta:
        model = CourseRating
        fields = ['id', 'course_title', 'learner', 'rating', 'lesson']

    def get_lesson_count(self, instance):
        return Lesson.objects.filter(course=instance.course).count()
    

    def get_course_status(self, instance):
        learner_package = instance.learner_user.first()
        return learner_package.courese_status

class GETSingleCourseSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  
    class Meta:
        model = Course
        fields = ['id', 'user', 'description', 'price', 'refund_policy', 'lesson_numbers', 'created_at', 'updated_at']

class SingleCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields =[ 'user', 'description', 'price', 'lesson_numbers', 'refund_policy']

    def get_course_status(self, instance):
        learner_package = instance.learner_user.first()
        return learner_package.courese_status

 
class LessonRatingSerializer(serializers.ModelSerializer):
    learner = serializers.CharField(source="user.full_name", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)
    lesson = serializers.SerializerMethodField()  

    class Meta:
        model = CourseRating
        fields = ['id', 'course_title', 'learner', 'rating', 'lesson']

    def get_lesson_count(self, instance):
        return Lesson.objects.filter(course=instance.course).count()
    


class GETSingleCourseSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  
    class Meta:
        model = Course
        fields = ['id', 'user', 'description', 'price', 'refund_policy', 'lesson_numbers', 'created_at', 'updated_at']

class SingleCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields =[ 'user', 'description', 'price', 'lesson_numbers', 'refund_policy']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id','title','image']
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'image']

class SchoolPackageDetailSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True)
    lesson_details = serializers.SerializerMethodField()
    class Meta:
        model = Package
        fields = ['id', 'name', 'price', 'total_course_hour', 'lesson_numbers', 'free_pickup', 'services', 'lesson_details']

    def get_lesson_details(self, instance):
        course = Course.objects.filter(user=instance.user).first()
        course_lessons = Lesson.objects.filter(course=course)[:instance.lesson_numbers]
        return LessonSerializer(course_lessons, many=True).data

    

class CoursesUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'user_type', 'full_name', 'logo']

class CoursesListSerializer(serializers.ModelSerializer):
    user = CoursesUserSerializer()
    course_lesson = serializers.SerializerMethodField()
    class Meta:
        model = LearnerSelectedPackage
        fields = ['id', 'user', 'start_date', 'attended_lesson', 'courese_status', 'course_lesson']


    def get_course_lesson(self, instance):
        course = instance.package.course_set.first()
        return course.lesson_numbers if course else 0
        
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['course', 'title', 'image']

class SchoolPackageDetailSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True)
    lesson_details = serializers.SerializerMethodField()
    class Meta:
        model = Package
        fields = ['id', 'name', 'price', 'total_course_hour', 'lesson_numbers', 'free_pickup', 'services', 'lesson_details']

    def get_lesson_details(self, instance):
        course = Course.objects.filter(user=instance.user).first()
        course_lessons = Lesson.objects.filter(course=course)[:instance.lesson_numbers]
        return LessonSerializer(course_lessons, many=True).data
