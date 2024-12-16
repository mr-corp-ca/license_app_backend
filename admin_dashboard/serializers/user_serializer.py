from admin_dashboard.serializers.utils_serializer import AdminCitySerializer, AdminProvinceSerializer
from rest_framework import serializers
from user_management_app.models import User



class DefaultAdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'phone_number', 'email', 'user_type', 'logo', 'dob', 'username']


class AdminNewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'username', 'email', 'user_type', 'logo']




class AdminUserGetSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()
    occupation = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'full_name', 'phone_number', 'username', 'email', 'user_type', 'logo', 'dob', 'date_joined', 'city', 'province', 'occupation']

    def get_city(self, instance):
        if instance.city:
            return AdminCitySerializer(instance.city).data
        else:
            return None

    def get_province(self, instance):
        if instance.province:
            return AdminProvinceSerializer(instance.province).data
        else:
            return None
        
    def get_occupation(self, instance):
        return 'Soft Engineer'