from django.db import models
from utils_app.models import BaseModelWithCreatedInfo
from user_management_app.constants import *
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
    logo = models.ImageField(upload_to='media/logo', null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    license_number = models.CharField(max_length=255, null=True, blank=True)
    province = models.ForeignKey('utils_app.Province', on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey('utils_app.City', on_delete=models.SET_NULL, null=True, blank=True)
    social_platform = models.CharField(max_length=255, choices=SOCIAL_PLATFORM_CHOICES, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
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
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_CHOICES)

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} to {self.wallet.user.username} Wallet"
    

class UserNotification(BaseModelWithCreatedInfo):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES)
    noti_type = models.CharField(max_length=255, choices=NOTIFICATION_TYPE_CHOICES) 
    description = models.TextField() 