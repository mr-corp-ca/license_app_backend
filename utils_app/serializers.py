from rest_framework import serializers
from .models import *
from user_management_app.models import *
from course_management_app.models import *
from timing_slot_app.models  import *
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']

class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['id', 'name']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'location_name', 'latitude', 'longitude']


class RadiusSerializer(serializers.ModelSerializer):
    locations = LocationSerializer(many=True, read_only=True)

    class Meta:
        model = Radius
        fields = ['id', 'main_location_name', 'main_latitude', 'main_longitude', 'locations']


class CreateRadiusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Radius
        fields = ['id','user', 'main_location_name', 'main_latitude', 'main_longitude']

class CoursePurchaseReceiptSerializer(serializers.ModelSerializer):
    institute_name = serializers.SerializerMethodField()
    institute_image = serializers.SerializerMethodField()
    date_purchased = serializers.SerializerMethodField()
    instructor_name = serializers.SerializerMethodField()
    vehicle_name = serializers.SerializerMethodField()
    vehicle_image = serializers.SerializerMethodField()
    pickup_location = serializers.SerializerMethodField()
    payment_method = serializers.SerializerMethodField()
    car_hired_request = serializers.SerializerMethodField()
    GST = serializers.SerializerMethodField()
    attended_lesson = serializers.IntegerField(read_only=True)

    purchased_plan = serializers.SerializerMethodField()

    class Meta:
        model = LearnerSelectedPackage
        fields = [
            'institute_name',
            'institute_image',
            'date_purchased',
            'attended_lesson',
            'instructor_name',
            'vehicle_name',
            'vehicle_image',
            'pickup_location',
            'payment_method',
            'car_hired_request',
            'GST',
            'purchased_plan',
        ]

    def get_institute_name(self, obj):
        school = obj.package.user.schoolprofile
        return school.institute_name if school else None
   
    def get_instructor_name(self, obj):
        school = obj.package.user.schoolprofile
        return school.instructor_name if school else None
    
    def get_date_purchased(self, obj):
        return obj.start_date.strftime('%d %b, %Y') if obj.start_date else None

    def get_vehicle_name(self, obj):
        # Assuming LearnerSelectedPackage relates to LearnerBookingSchedule through user
        booking_schedule = LearnerBookingSchedule.objects.filter(user=obj.user).last()
        if booking_schedule and booking_schedule.vehicle:
            return booking_schedule.vehicle.name
        return "No vehicle information available"

    def get_vehicle_image(self, obj):
        booking_schedule = LearnerBookingSchedule.objects.filter(user=obj.user).last()
        if booking_schedule and booking_schedule.vehicle:
            return booking_schedule.vehicle.image.url

    def get_pickup_location(self, obj):
        learner = obj.user
        # Ensure that `vehicle` attribute is correctly referenced, it might be related through booking
        booking_schedule = LearnerBookingSchedule.objects.filter(user=obj.user).last()
        if booking_schedule and booking_schedule.vehicle:
            vehicle_user = booking_schedule.vehicle.user
            print("vehicle_user",vehicle_user)
            locations = Location.objects.filter(radius__user=vehicle_user)
            print("locations",locations)
            if locations:
                # Serialize and return locations
                serialized_locations = LocationSerializer(locations, many=True).data
                return serialized_locations
        
        # If no locations are found, fallback to learner's address
        if learner.city and learner.province:
            return f"{learner.address}, {learner.city.name}, {learner.province.name}"
        
        return None

    def get_payment_method(self, obj):
        transaction = TransactionHistroy.objects.filter(wallet__user=obj.user).last()
        return transaction.payment_method if transaction else None

    def get_car_hired_request(self, obj):
        # Check the hire car request for the learner
        booking = LearnerBookingSchedule.objects.filter(user=obj.user, hire_car=True).first()

        if booking:
            if booking.hire_car_status == "Rejected":
                return "Request Rejected"
            elif booking.hire_car_price_paid:
                return "Paid ($32)"
            elif booking.hire_car_status == "Pending":
                return "Pending ($32)"
        return None

    def get_GST(self, obj):
        return "5%"  # Static value

    def get_purchased_plan(self, obj):
        return f"{obj.package.name} (${obj.package.price})"

    def get_institute_image(self, obj):
        school = obj.package.user
        return school.logo.url if school and school.logo else None

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'
