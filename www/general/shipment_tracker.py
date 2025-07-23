#!/usr/bin/env python

# This script requires the 'requests' and 'beautifulsoup4' libraries.
# You can install them by running: pip install requests beautifulsoup4

import requests
import time
import subprocess
import os
import sys
from bs4 import BeautifulSoup

# --- Configuration ---
TRACKING_URL = "https://www.bluedart.com/trackdartresultthirdparty?trackFor=0&trackNo=90152954290"
STATUS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shipment_status.txt")
CHECK_INTERVAL_SECONDS = 300  # 5 minutes

def get_parsed_status():
    """Fetches and parses the shipment status from the tracking page."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(TRACKING_URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the status
        status_label = soup.find('label', string='Status ')
        status = "Not found"
        if status_label:
            status_p = status_label.find_next_sibling('p')
            if status_p:
                status = status_p.get_text(strip=True)

        # Find the latest activity in the shipment journey table
        latest_activity = "Not found"
        panel_body = soup.find('div', class_='panel-body')
        if panel_body:
            tables = panel_body.find_all('table', class_='table-bordered')
            for table in tables:
                tbody = table.find('tbody')
                if tbody:
                    first_row = tbody.find('tr')
                    if first_row:
                        cells = first_row.find_all('td')
                        if len(cells) >= 4:
                            location = cells[0].get_text(strip=True)
                            detail = cells[1].get_text(strip=True)
                            date = cells[2].get_text(strip=True)
                            time = cells[3].get_text(strip=True)
                            latest_activity = f"{location}: {detail} on {date} at {time}"
                            # Break the loop once we have the latest activity
                            break

        return f"Status: {status} | Latest Activity: {latest_activity}"

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None
    except Exception as e:
        print(f"An error occurred during parsing: {e}")
        return None

def get_last_status():
    """Reads the last known status from a file."""
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return f.read()
    return ""

def save_last_status(status):
    """Saves the current status to a file."""
    with open(STATUS_FILE, "w") as f:
        f.write(status)

def send_termux_notification(message):
    """Sends a notification using termux-notification."""
    try:
        subprocess.run(
            ["termux-notification", "--title", "Shipment Update", "--content", message],
            check=True
        )
    except FileNotFoundError:
        print("'termux-notification' command not found. Please ensure you are running this on Termux and have Termux:API installed.")
    except subprocess.CalledProcessError as e:
        print(f"Error sending notification: {e}")

def main():
    """Main loop to check for shipment status changes."""

    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("--- Running in Test Mode ---")
        status = get_parsed_status()
        print(status)
        return

    print("Starting shipment tracker...")
    last_status = get_last_status()
    if not last_status:
        print("No previous status found. Will notify on first successful fetch.")

    while True:
        print("Checking for shipment updates...")
        current_status = get_parsed_status()

        if current_status:
            if current_status != last_status:
                print(f"Shipment status has changed! New status: {current_status}")
                send_termux_notification(f"New status: {current_status}")
                save_last_status(current_status)
                last_status = current_status
            else:
                print("No change in shipment status.")
        else:
            print("Could not retrieve shipment status.")

        print(f"Waiting for {CHECK_INTERVAL_SECONDS} seconds before next check...")
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
