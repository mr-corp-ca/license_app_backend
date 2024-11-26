from django.db import models

from user_management_app.models import User
from utils_app.models import BaseModelWithCreatedInfo

# Create your models here.


class Course(BaseModelWithCreatedInfo):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=255, help_text="Title of the course")
    description = models.TextField(help_text="Detailed description of the course")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price of the course in USD")
    license_category = models.CharField(max_length=100, help_text="Category of the license, e.g., Professional, Educational")
    services = models.TextField(help_text="List of services included in the course", blank=True, null=True)
    lesson_numbers = models.PositiveIntegerField(help_text="Number of lessons in the course")
    refund_policy = models.TextField(help_text="Details of the refund policy", blank=True, null=True)
    course_cover_image = models.ImageField(upload_to='course_images/', help_text="Cover image for the course", blank=True, null=True)

    def __str__(self):
        return self.title
    


class Vehicle(BaseModelWithCreatedInfo):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=255, verbose_name="Vehicle Name")
    trainer_name = models.CharField(max_length=255, verbose_name="Trainer Name")
    vehicle_registration_no = models.CharField(max_length=100, unique=True, verbose_name="Registration Number")
    license_number = models.CharField(max_length=100, unique=True, verbose_name="License Number")
    vehicle_model = models.CharField(max_length=100, verbose_name="Vehicle Model")
    image = models.ImageField(upload_to='vehicle_images/', blank=True, null=True, verbose_name="Vehicle Image")

    def __str__(self):
        return f"{self.name} ({self.vehicle_registration_no})"