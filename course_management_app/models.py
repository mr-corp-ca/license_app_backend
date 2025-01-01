from django.db import models

from course_management_app.constants import AUDIENCE_CHOICES, OFFER_TYPE_CHOICES, COURSE_STATUS_CHOICES
from user_management_app.models import User
from utils_app.models import BaseModelWithCreatedInfo

# Create your models here.

class LicenseCategory(BaseModelWithCreatedInfo):
    name = models.CharField(max_length=255)

class Service(BaseModelWithCreatedInfo):
    name = models.CharField(max_length=255)

class Course(BaseModelWithCreatedInfo):
    user = models.ForeignKey('user_management_app.User', on_delete=models.CASCADE, related_name='course_user')
    lesson = models.ManyToManyField('course_management_app.Lesson', related_name='course_lessons',default=None)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True, verbose_name='About')
    price = models.FloatField(default=0.0, verbose_name='price per lesson')
    lesson_numbers = models.PositiveIntegerField()
    refund_policy = models.TextField(blank=True, null=True)
    # course_cover_image = models.ImageField(upload_to='course_images/', blank=True, null=True)

    def __str__(self):
        return self.user.full_name

class Lesson(BaseModelWithCreatedInfo):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='Lesson/images')

    def __str__(self):
        return self.title


class Vehicle(BaseModelWithCreatedInfo):
    VEHICLE_STATUS_CHOICES = [
        ('free', 'Free'),
        ('booked', 'Booked'),
    ]
    user = models.ForeignKey('user_management_app.User', on_delete=models.CASCADE,related_name='user_vehicle')
    instructor = models.ForeignKey('user_management_app.User',on_delete=models.CASCADE, null=True, blank=True, related_name='instructor_vehicle')

    name = models.CharField(max_length=255, verbose_name="Vehicle Name")
    trainer_name = models.CharField(max_length=255, null=True, blank=True ,verbose_name="Trainer Name")
    vehicle_registration_no = models.CharField(max_length=100, unique=True, verbose_name="Registration Number")
    license_number = models.CharField(max_length=100, unique=True, verbose_name="License Number")
    vehicle_model = models.CharField(max_length=100, verbose_name="Vehicle Model")
    image = models.ImageField(upload_to='vehicle_images/', blank=True, null=True, verbose_name="Vehicle Image")
    booking_status = models.CharField(max_length=10,choices=VEHICLE_STATUS_CHOICES,default='free',verbose_name="Vehcile Status")


    def __str__(self):
        return f"{self.name} ({self.vehicle_registration_no})"

class Package(BaseModelWithCreatedInfo):
    user = models.ForeignKey('user_management_app.User', on_delete=models.CASCADE, related_name='package_user')

    name = models.CharField(max_length=255, verbose_name="Package Name")
    price = models.FloatField(default=0.0, verbose_name="Package Price")
    total_course_hour = models.CharField(max_length=255, verbose_name="Total Course Hour")
    lesson_numbers = models.PositiveIntegerField(verbose_name="Lesson Number")
    free_pickup = models.FloatField(default=0.0, verbose_name="Free Pickup")
    services = models.ManyToManyField(Service, related_name='package_services', blank=True)

class DiscountOffer(BaseModelWithCreatedInfo):
    offer_type = models.CharField(max_length=255, verbose_name="Package Name", choices=OFFER_TYPE_CHOICES)
    name = models.CharField(max_length=255, verbose_name="Package Name")
    audience = models.CharField(max_length=255, verbose_name="Package Name", choices=AUDIENCE_CHOICES)
    
    user = models.ForeignKey('user_management_app.User', on_delete=models.CASCADE, related_name='discountooffer_user')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    discount = models.PositiveIntegerField(default=0, verbose_name="Discount & offers(%)")
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")


class Certificate(BaseModelWithCreatedInfo):
    name = models.CharField(max_length=255)
    date = models.DateField()
    about = models.TextField(null=True, blank=True)
    signature = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='logos/')
    image = models.ImageField(upload_to='certificate/', null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    created_by = models.ForeignKey('user_management_app.User', on_delete=models.CASCADE, related_name='certificate_user')

    def __str__(self):
        return self.name


class UserSelectedCourses(BaseModelWithCreatedInfo):
    user = models.OneToOneField('user_management_app.User', on_delete=models.CASCADE, related_name='course_profile')
    courses = models.ManyToManyField(Course, related_name='user_profiles')

    def __str__(self):
        return f"Profile of {self.user.username}"
    

class SubscriptionPackagePlan(BaseModelWithCreatedInfo):
    PACKAGE_PLAN_CHOICE = [
        ('month','Month'),
        ('half-year','Six-Month'),

        ('year','Year'),
    ]

    price = models.FloatField(default=0.0,verbose_name='Subscription Price')
    package_plan = models.CharField(max_length=255,choices=PACKAGE_PLAN_CHOICE,verbose_name='Subscription plan')


class SelectedSubscriptionPackagePaln(BaseModelWithCreatedInfo):
    user = models.ForeignKey('user_management_app.User', on_delete=models.CASCADE, related_name='subscription_user')
    package_plan = models.ForeignKey(SubscriptionPackagePlan, on_delete=models.CASCADE)
    expired = models.DateTimeField(verbose_name='Package Expired')

class LearnerSelectedPackage(BaseModelWithCreatedInfo):
    user = models.ForeignKey('user_management_app.User', on_delete=models.CASCADE, related_name='learner_user')

    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='learnerselectedpackage_package')
    attended_lesson = models.PositiveIntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    courese_status = models.CharField(max_length=255, choices=COURSE_STATUS_CHOICES, default='on-going')



class CourseRating(BaseModelWithCreatedInfo):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_rating')
    user = models.ForeignKey('user_management_app.User', on_delete=models.CASCADE, related_name='course_user_rating')
    rating = models.PositiveIntegerField(default=0)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    learner_selected_package = models.PositiveIntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    courese_status = models.CharField(max_length=255, choices=COURSE_STATUS_CHOICES, default='on-going')

    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    learner_selected_package = models.PositiveIntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)


class LogsModel(BaseModelWithCreatedInfo):
    json_data = models.TextField()


class CourseRating(BaseModelWithCreatedInfo):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_rating')
    user = models.ForeignKey('user_management_app.User', on_delete=models.CASCADE, related_name='course_user_rating')
    rating = models.PositiveIntegerField(default=0)

