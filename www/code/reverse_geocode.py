
import json
import os
import requests

def get_location():
    """Gets the current location using termux-location."""
    location_str = os.popen("termux-location").read()
    try:
        return json.loads(location_str)
    except json.JSONDecodeError:
        return {}

def reverse_geocode(latitude, longitude):
    """Gets the address for a given latitude and longitude using OpenStreetMap."""
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"
    headers = {
        'User-Agent': 'GeminiCLI/1.0'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    except json.JSONDecodeError:
        print("Failed to decode JSON response.")
        return None

if __name__ == "__main__":
    location = get_location()
    latitude = location.get("latitude")
    longitude = location.get("longitude")

    if latitude and longitude:
        address_data = reverse_geocode(latitude, longitude)
        if address_data:
            print(address_data.get("display_name", "Could not find address."))
        else:
            print("Could not retrieve address information.")
    else:
        print("Could not get location.")
