from django.contrib import admin

from course_management_app.models import Course, DiscountOffer, Lesson, Package, Vehicle, Service, LicenseCategory

# Register your models here.


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'lesson_numbers', 'user', 'created_at')
    search_fields = ('title', 'license_category', 'price', 'lesson_numbers', 'user__username', 'user__full_name', 'user__email',  'user__first_name', 'user__last_name')
    list_filter = ('license_category', 'created_at')
    ordering = ('-created_at',)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'trainer_name', 'vehicle_registration_no', 'license_number', 'vehicle_model', 'user', 'created_at')
    search_fields = ('name', 'trainer_name', 'vehicle_registration_no', 'license_number', 'vehicle_model', 'user__username', 'user__full_name', 'user__email',  'user__first_name', 'user__last_name')
    list_filter = ('vehicle_model',)
    ordering = ('-created_at',)

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'price', 'total_course_hour', 'lesson_numbers', 'created_at')
    search_fields = ('name', 'price', 'total_course_hour', 'lesson_numbers', 'user__username', 'user__full_name', 'user__email',  'user__first_name', 'user__last_name')
    ordering = ('-created_at',)

@admin.register(DiscountOffer)
class DiscountOfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'offer_type', 'name', 'audience', 'user', 'course', 'discount', 'start_date', 'end_date', 'created_at')
    search_fields = ('offer_type', 'name', 'audience', 'course', 'discount', 'user__username', 'user__full_name', 'user__email',  'user__first_name', 'user__last_name')
    ordering = ('-created_at',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course', 'image')
    search_fields = ('title','course__title')
    ordering = ('-created_at',)


@admin.register(LicenseCategory)
class LicenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
