from django.db import models
from django.apps import apps
from course_management_app.constants import AUDIENCE_CHOICES, OFFER_TYPE_CHOICES, COURSE_STATUS_CHOICES,PACKAGE_PLAN_CHOICE, PACKAGE_STATUS
from utils_app.models import BaseModelWithCreatedInfo
from user_management_app.threads import send_push_notification
import stripe

from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY
# Create your models here.

class LicenseCategory(BaseModelWithCreatedInfo):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Service(BaseModelWithCreatedInfo):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Course(BaseModelWithCreatedInfo):
    user = models.ForeignKey('user_management_app.User', on_delete=models.CASCADE, related_name='course_user')
    lesson = models.ManyToManyField('course_management_app.Lesson', related_name='course_lessons',default=None)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True, null=True, verbose_name='About')
    price = models.FloatField(default=0.0, verbose_name='price per lesson')
    road_test_price = models.PositiveIntegerField(null=True, blank=True)
    lesson_numbers = models.PositiveIntegerField()
    refund_policy = models.TextField(blank=True, null=True)
    course_cover_image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    service = models.ManyToManyField(Service, related_name='course_service', default=None)
    
    def __str__(self):
        return self.user.username

class Lesson(BaseModelWithCreatedInfo):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='Lesson/images')
    is_deleted =  models.BooleanField(default=False)

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
    courses = models.ManyToManyField(Course, related_name='user_profiles', blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
    

class SubscriptionPackagePlan(BaseModelWithCreatedInfo):
    price = models.FloatField(default=0.0,verbose_name='Subscription Price')
    package_plan = models.CharField(max_length=255,choices=PACKAGE_PLAN_CHOICE,verbose_name='Subscription plan')


class SelectedSubscriptionPackagePaln(BaseModelWithCreatedInfo):
    user = models.ForeignKey('user_management_app.User', on_delete=models.CASCADE, related_name='subscription_user')
    package_plan = models.ForeignKey(SubscriptionPackagePlan, on_delete=models.CASCADE)
    expired = models.DateTimeField(verbose_name='Package Expired')
    package_status =  models.CharField(max_length=255, choices=PACKAGE_STATUS, default='pending')
    stripe_secret_id = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        TransactionHistroy = apps.get_model('user_management_app', 'TransactionHistroy')

        if self.package_status == 'accepted' and self.stripe_secret_id:
            try:
                intent = stripe.PaymentIntent.retrieve(self.stripe_secret_id)

                if intent.status == 'succeeded':
                    TransactionHistroy.objects.create(
                        school=self.user,
                        wallet=self.user.wallet,
                        amount=self.package_plan.price,
                        payment_method='stripe',
                        transaction_type='deposit',
                        transaction_status='accepted'
                    )
                    self.package_status = 'accepted'
                    super().save(*args, **kwargs)  
                    send_push_notification(
                        self.user,
                        "Subscription Approved",
                        f"Your subscription for {self.package_plan.package_plan} has been successfully activated.",
                        "accepted"
                    )

                else:
                    self.package_status = 'rejected'
                    super().save(*args, **kwargs)
                    send_push_notification(
                        self.user,
                        "Subscription Rejected",
                        "Your subscription payment failed. Please try again.",
                        "rejected"
                    )

            except stripe.error.CardError:
                self.package_status = 'rejected'
                super().save(*args, **kwargs)
                send_push_notification(
                    self.user,
                    "Subscription Rejected",
                    "Your payment card was declined. Please use a different card.",
                    "rejected"
                )

            except stripe.error.StripeError as e:
                self.package_status = 'rejected'
                super().save(*args, **kwargs)
                send_push_notification(
                    self.user,
                    "Subscription Error",
                    f"Payment failed due to Stripe error: {str(e)}",
                    "rejected"
                )

        elif self.package_status == 'rejected':
            send_push_notification(
                self.user,
                "Subscription Rejected",
                "Your subscription request has been rejected by the admin.",
                "rejected"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.full_name} - {self.package_plan.package_plan} ({self.package_status})"

class LearnerSelectedPackage(BaseModelWithCreatedInfo):
    user = models.ForeignKey('user_management_app.User', on_delete=models.CASCADE, related_name='learner_user')

    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='learnerselectedpackage_package')
    attended_lesson = models.PositiveIntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    courese_status = models.CharField(max_length=255, choices=COURSE_STATUS_CHOICES, default='on-going')

class SchoolRating(BaseModelWithCreatedInfo):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_rating')
    user = models.ForeignKey('user_management_app.User', on_delete=models.CASCADE, related_name='course_user_rating')
    rating = models.PositiveIntegerField(default=0)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    learner_selected_package = models.PositiveIntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)


class GeneralPolicy(BaseModelWithCreatedInfo):
    about = models.TextField(null=True, blank=True, verbose_name='About')    
    refund_policy = models.TextField(null=True, blank=True,verbose_name='Refund_Policy')


class InstructorLesson(BaseModelWithCreatedInfo):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="instructor_lessons")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="instructor_lessons")
