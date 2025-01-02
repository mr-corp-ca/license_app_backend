from rest_framework import serializers
from .models import *

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
