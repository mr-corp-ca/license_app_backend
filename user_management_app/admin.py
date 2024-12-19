from django.contrib import admin
from user_management_app.models import *
# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'user_type']
    search_fields = ('username', 'full_name', 'email',  'first_name', 'last_name')
    ordering = ('-date_joined',)

@admin.register(UserVerification)
class UserVerificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'code', 'is_varified']
    search_fields = ('user__username', 'user__full_name', 'user__email',  'user__first_name', 'user__last_name')

    ordering = ('-created_at',)

@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'institude_name', 'trainer_name', 'license_no', 'total_lesson', 'price']
    search_fields = ('user__username', 'user__full_name', 'user__email',  'user__first_name', 'user__last_name', 'institude_name', 'trainer_name', 'license_no')
    ordering = ('-created_at',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'rating', 'feedback', 'user', 'created_at']
    search_fields = ('user__username', 'user__full_name', 'user__email',  'user__first_name', 'user__last_name')
    ordering = ('-created_at',)

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'balance']
    search_fields = ('user__username', 'user__full_name', 'user__email',  'user__first_name', 'user__last_name')
    ordering = ('-created_at',)

@admin.register(TransactionHistroy)
class TransactionHistroyAdmin(admin.ModelAdmin):
    list_display = ['id', 'wallet', 'amount', 'transaction_type']
    search_fields = ('wallet__user__username', 'wallet__user__full_name', 'wallet__user__email',  'wallet__user__first_name', 'wallet__user__last_name')

    ordering = ('-created_at',)

@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at']
    search_fields = ('user__username', 'user__full_name', 'user__email',  'user__first_name', 'user__last_name')
    ordering = ('-created_at',)

admin.site.register(SchoolSetting)