from django.db import models
# from course_management_app.models import Course
from utils_app.models import BaseModelWithCreatedInfo
from django.utils.timezone import now
from datetime import timedelta
from django.utils.text import slugify
from user_management_app.constants import *
from course_management_app.models import *
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class MyAccountManager(BaseUserManager):
    def create_user(self, phone_number, username, password=None):
        if not phone_number:
            raise ValueError('Users must have a phone_number.')
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            phone_number=phone_number,
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, username, password):
        user = self.create_user(
            phone_number=phone_number,
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    full_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=255, unique=True, null=True, blank=True)
    email = models.EmailField(verbose_name="email", max_length=60, unique=True, null=True, blank=True)
    user_type = models.CharField(max_length=255,  choices=USER_TYPE_CHOICES)
    address = models.CharField(max_length=255,null=True,blank=True)
    logo = models.ImageField(upload_to='media/logo', null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    license_number = models.CharField(max_length=255, null=True, blank=True)
    province = models.ForeignKey('utils_app.Province', on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey('utils_app.City', on_delete=models.SET_NULL, null=True, blank=True)
    social_platform = models.CharField(max_length=255, choices=SOCIAL_PLATFORM_CHOICES, null=True, blank=True)
    user_status = models.CharField(max_length=255,  choices=USER_STATUS_CHOICES, default='pending', null=True, blank=True)
    lat = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True, 
        help_text="Latitude"
    )
    long = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True, 
        help_text="Longitude"
    )

    is_deleted = models.BooleanField(default=False)
    deletd_reason =  models.CharField(max_length=255, choices=DELETED_REASON, null=True, blank=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone_number']

    objects = MyAccountManager()

    def __str__(self):
        return self.username

    # Using Django's default permissions management
    def has_perm(self, perm, obj=None):
        return super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        return super().has_module_perms(app_label)
        return True

    def __str__(self):
        return self.username

class UserVerification(BaseModelWithCreatedInfo):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=28, null=True, blank=True)
    is_varified = models.BooleanField(default=False)

class Review(BaseModelWithCreatedInfo):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    feedback = models.TextField(max_length=1000, null=True, blank=True)
    def __str__(self):
        return f"Rating: {self.rating}"


class DriverProfile(BaseModelWithCreatedInfo):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_logo = models.ImageField(upload_to='media/driver/logo')
    institude_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    institude_image = models.ImageField(upload_to='media/driver/institude_image')
    trainer_name = models.CharField(max_length=255)
    license_no = models.CharField(max_length=255) 
    address = models.TextField() 
    total_lesson = models.IntegerField() 
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self): 
        return self.institude_name

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"


class Wallet(BaseModelWithCreatedInfo):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.user.username} wallet"


class TransactionHistroy(BaseModelWithCreatedInfo):
    school =  models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='School_transaction_History')
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    payment_method = models.CharField(max_length=20, blank=True, null=True ,choices=TRANSACTION_METHOD)
    transaction_type = models.CharField(max_length=15, choices=TRANSACTION_CHOICES)
    transaction_status = models.CharField(max_length=15, choices=TRANSACTION_STATUS,  blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} to {self.wallet.user.username} Wallet"
    

class UserNotification(BaseModelWithCreatedInfo):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transactionhistory = models.ForeignKey(TransactionHistroy, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, null=True, blank=True)
    noti_type = models.CharField(max_length=255, choices=NOTIFICATION_TYPE_CHOICES) 
    title = models.CharField(max_length=255, null=True, blank=True) 
    text = models.TextField(null=True, blank=True) 


class SchoolSetting(BaseModelWithCreatedInfo):
    user =  models.OneToOneField(User,on_delete=models.CASCADE, related_name='School_user')
    instructor = models.ManyToManyField(User, related_name='School_instructor', blank=True)
    learner = models.ManyToManyField(User, related_name='School_learner', blank=True)

    def __str__(self):
        return str(self.user)
    
class LearnerReport(BaseModelWithCreatedInfo):
    learner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="learner" ,related_name='learnerreport_learner')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="school" ,related_name='learnerreport_instructor')
    reported_by = models.CharField(max_length=10, choices=REPORTER_CHOICES, default='learner')
    instructor_reason = models.CharField(max_length=255, null=True, blank=True, choices=INSTRUCTOR_REPORT_REASONS)
    description = models.TextField(null=True, blank=True)
    learner_reason = models.CharField(max_length=255, null=True, blank=True, choices=LEARNER_REPORT_RESONS)

    def __str__(self):
        if self.reported_by == 'learner':
            return f"Report by {self.learner.username} against {self.instructor.username} - Reason: {self.learner_reason}"
        elif self.reported_by == 'school':
            return f"Report by {self.instructor.username} against {self.learner.username} - Reason: {self.instructor_reason}"
        return f"Report for {self.learner.username} - No Reason Provided"

# class InstructorProfile(BaseModelWithCreatedInfo):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     institute_name = models.CharField(max_length=255,null=True,blank=True)
#     institute_image = models.ImageField(upload_to='media/institute_image')
#     description = models.TextField(null=True, blank=True)

#     def __str__(self) :
#         return f"Institute Name {self.institute_name}"
 

class SchoolProfile(BaseModelWithCreatedInfo):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license_category = models.ManyToManyField('course_management_app.LicenseCategory', blank=True)
    services = models.ManyToManyField('course_management_app.Service', blank=True)

    institute_name = models.CharField(max_length=255, null=True, blank=True)
    instructor_name = models.CharField(max_length=255, null=True, blank=True)
    registration_file = models.FileField(upload_to='media/school/registration_file', null=True, blank=True)


class Referral(BaseModelWithCreatedInfo):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="referral")
    unique_code = models.SlugField(unique=True, blank=True, null=True, help_text="This code is for institute")
    learner_code = models.SlugField(unique=True, blank=True, null=True, help_text="This code is for learner")
    joined_by = models.CharField(max_length=255, blank=True, null=True, help_text="Code of the user who referred this user.")
    invited_users = models.ManyToManyField(User, related_name="invited_by", blank=True)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_REFERRAL_TYPE, default='learner')
    referral_count = models.IntegerField(default=0) 

    def generate_next_code(self, last_code):
            """Helper function to increment GEARUP code"""
            if last_code and last_code.startswith("GEARUP"):
                try:
                    number = int(last_code.replace("GEARUP", ""))
                    return f"GEARUP{number + 1:04}"
                except ValueError:
                    pass
            return "GEARUP0001"

    def save(self, *args, **kwargs):
        if not self.learner_code or not self.unique_code:
            latest_referral = Referral.objects.order_by('-id').first()

            # Start with GEARUP0001 if no objects exist
            last_learner_code = latest_referral.learner_code if latest_referral and latest_referral.learner_code else None
            last_unique_code = latest_referral.unique_code if latest_referral and latest_referral.unique_code else None

            new_learner_code = self.generate_next_code(last_learner_code)
            new_unique_code = self.generate_next_code(new_learner_code)  # ensure it's always different

            # Ensure uniqueness and difference
            while Referral.objects.filter(learner_code=new_learner_code).exists():
                new_learner_code = self.generate_next_code(new_learner_code)

            while Referral.objects.filter(unique_code=new_unique_code).exists() or new_unique_code == new_learner_code:
                new_unique_code = self.generate_next_code(new_unique_code)

            self.learner_code = new_learner_code
            self.unique_code = new_unique_code

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Referral Code"


class DiscountCoupons(BaseModelWithCreatedInfo):
    school = models.ForeignKey(User, on_delete=models.CASCADE, related_name="discount_offer_user", verbose_name="school", null=True, blank=True)
    calling_agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="discount_buyer_user", verbose_name='Calling Agent')
    package = models.ForeignKey(SubscriptionPackagePlan, on_delete=models.CASCADE, related_name="Subscribed_Package", verbose_name="Selected Subscription", null=True, blank=True)
    discount_price = models.FloatField(default=0.0, null=True, blank=True, help_text='Discount Price')
    is_used = models.BooleanField(default=False)
    code = models.CharField(max_length=20, null=True, blank=True, unique=True)
    expiration_time = models.PositiveIntegerField(default=24, help_text="Coupon validity in hours") 

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not DiscountCoupons.objects.filter(code=code).exists():
                return code

    def is_expired(self):
        """Check if the coupon is expired based on school-defined expiration time."""
        return now() > self.created_at + timedelta(hours=self.expiration_time)