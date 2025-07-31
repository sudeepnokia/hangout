#!/bin/bash
# This script is run by the widget. It must be very fast.

LOCATION_FILE="/storage/emulated/0/termux/hangout/www/code/current_location.txt"

# The only job of this script is to display the latest location from the file.
if [ -f "$LOCATION_FILE" ]; then
    cat "$LOCATION_FILE"
else
    echo "Waiting for location..."
fi
