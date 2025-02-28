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


@admin.register(SchoolProfile)
class SchoolProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'institute_name', 'instructor_name', 'created_at', 'updated_at')
    search_fields = ('user__username', 'institute_name', 'instructor_name')
    list_filter = ('license_category', 'services', 'created_at')

@admin.register(LearnerReport)
class LearnerReportAdmin(admin.ModelAdmin):
    list_display = ('reported_by','learner', 'instructor', 'learner_reason', 'instructor_reason', 'description', 'created_at')
    list_filter = ('reported_by', 'created_at', 'learner', 'instructor')
    search_fields = ('learner__username', 'instructor__username', 'learner_reason', 'instructor_reason', 'description')
    ordering = ('-created_at',)

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ("user", "unique_code", "joined_by", "total_earnings")
    search_fields = ("user__username", "unique_code", "joined_by")
    list_filter = ("total_earnings",)
    readonly_fields = ("unique_code",)


@admin.register(DiscountCoupons)
class DiscountCouponsAdmin(admin.ModelAdmin):
    list_display = ('code', 'school', 'calling_agent', 'package', 'discount_price', 'is_used', 'created_at', 'expiration_time')
    search_fields = ('code', 'school__full_name', 'calling_agent__full_name', 'package__package_plan__package_plan')
    list_filter = ('is_used', 'expiration_time', 'created_at')
    readonly_fields = ('code', 'created_at')
    ordering = ('-created_at',)

    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = "Expired?"
