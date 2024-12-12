from django.db import models

from course_management_app.constants import AUDIENCE_CHOICES, OFFER_TYPE_CHOICES
from user_management_app.models import User
from utils_app.models import BaseModelWithCreatedInfo

# Create your models here.


class LicenseCategory(BaseModelWithCreatedInfo):
    name = models.CharField(max_length=255)

class Service(BaseModelWithCreatedInfo):
    name = models.CharField(max_length=255)

class Course(BaseModelWithCreatedInfo):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    license_category = models.ManyToManyField(LicenseCategory, related_name='course_license_category', blank=True)
    services = models.ManyToManyField(Service, related_name='course_services', blank=True)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField(default=0.0)
    lesson_numbers = models.PositiveIntegerField()
    refund_policy = models.TextField(blank=True, null=True)
    course_cover_image = models.ImageField(upload_to='course_images/')

    def __str__(self):
        return self.title

class Lesson(BaseModelWithCreatedInfo):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='Lession/images')

class Vehicle(BaseModelWithCreatedInfo):
    VEHICLE_STATUS_CHOICES = [
        ('free', 'Free'),
        ('booked', 'Booked'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=255, verbose_name="Vehicle Name")
    trainer_name = models.CharField(max_length=255, verbose_name="Trainer Name")
    vehicle_registration_no = models.CharField(max_length=100, unique=True, verbose_name="Registration Number")
    license_number = models.CharField(max_length=100, unique=True, verbose_name="License Number")
    vehicle_model = models.CharField(max_length=100, verbose_name="Vehicle Model")
    image = models.ImageField(upload_to='vehicle_images/', blank=True, null=True, verbose_name="Vehicle Image")
    booking_status = models.CharField(max_length=10,choices=VEHICLE_STATUS_CHOICES,default='free',verbose_name="Vehcile Status")


    def __str__(self):
        return f"{self.name} ({self.vehicle_registration_no})"

class Package(BaseModelWithCreatedInfo):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    discount = models.PositiveIntegerField(default=0, verbose_name="Discount & offers(%)")
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")

class UserSelectedCourses(BaseModelWithCreatedInfo):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='course_profile')
    courses = models.ManyToManyField(Course, related_name='user_profiles')

    def __str__(self):
        return f"Profile of {self.user.username}"
