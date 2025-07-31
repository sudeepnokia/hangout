#!/usr/bin/env python
import json
import os
import requests
import time
import subprocess

LOCATION_FILE = "/storage/emulated/0/termux/hangout/www/code/current_location.txt"

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
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        return {"error": str(e)}

def force_widget_reload():
    """Executes the command to make Termux:Widget reload its widgets."""
    # This command tells the widget add-on to re-run all its widget scripts.
    subprocess.run(["termux-widget", "-r"])

if __name__ == "__main__":
    print("Starting auto-updating location script. Press Ctrl+C to stop.")
    while True:
        location = get_location()
        latitude = location.get("latitude")
        longitude = location.get("longitude")

        output_text = "Fetching location..."
        if latitude and longitude:
            address_data = reverse_geocode(latitude, longitude)
            if address_data and "error" not in address_data:
                output_text = address_data.get("display_name", "Could not find address.")
            else:
                output_text = address_data.get("error", "Geocoding failed.")
        
        # Write the latest result to the file
        with open(LOCATION_FILE, "w") as f:
            f.write(output_text)
        
        # Force the widget to refresh and show the new text
        force_widget_reload()
        
        # Wait for 60 seconds before the next update
        time.sleep(60)
