from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'user_type', 'mobile_number']

class UserGETSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'user_type', 'first_name', 'last_name', 'date_of_birth', 'license_no', 'full_name', 'mobile_number']


class DriverProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverProfile
        fields = ['user', 'user_logo', 'institude_name', 'description', 'institude_image', 'trainer_name', 'license_no', 'address', 'total_lesson', 'price']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'rating', 'feedback']

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'user', 'balance']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistroy
        fields = ['id', 'wallet', 'amount', 'transaction_type']
