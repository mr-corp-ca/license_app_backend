import os
import requests
import math


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points on the Earth using the Haversine formula.
    Returns the distance in kilometers.
    """
    try:
        R = 6371.0

        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return round(distance,2)
    
    except Exception as e:
        print("Radius Error: ", e)


def get_lat_lon_from_address(address):
    """
    Function to convert an address into latitude and longitude using Google Maps Geocoding API.
    """
    google_api_key = os.environ.get('GOOGLE_API_KEY')  
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={google_api_key}"
    
    response = requests.get(url)  
    print("Response============>",response)
    if response.status_code == 200:  
        data = response.json()
        if data['status'] == 'OK':  
            lat = data['results'][0]['geometry']['location']['lat']
            lon = data['results'][0]['geometry']['location']['lng']
            return lat, lon 
    return None, None  