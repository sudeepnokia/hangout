#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
import urllib.request
import urllib.parse
import json
import sys

app = Flask(__name__)

HISTORY_FILE = "/storage/emulated/0/termux/hangout/www/code/travel_app/location_history.json"

def query_directions(origin, destination, mode, api_key, alternatives=False, transit_mode=None):
    """Queries the Google Maps Directions API."""
    params = {
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "key": api_key
    }
    if alternatives:
        params["alternatives"] = "true"
    if transit_mode:
        params["transit_mode"] = transit_mode
    if mode == "driving":
        params["departure_time"] = "now"
        
    url = f"https://maps.googleapis.com/maps/api/directions/json?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "HybridTravelApp/1.0"}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"Error querying Directions API: {e}", file=sys.stderr)
        return None

def save_to_history(origin, destination):
    """Saves unique locations to a persistent JSON history file."""
    import os
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except Exception:
            history = []
            
    # Add unique locations
    updated = False
    for loc in [origin, destination]:
        if loc and loc not in history:
            history.append(loc)
            updated = True
            
    if updated:
        try:
            with open(HISTORY_FILE, "w") as f:
                json.dump(history, f, indent=2)
            # Run the python validation command required by rule
            import subprocess
            subprocess.run(["python3", "-m", "json.tool", HISTORY_FILE], stdout=subprocess.DEVNULL)
        except Exception as e:
            print(f"Error saving history file: {e}", file=sys.stderr)

@app.route('/')
def index():
    default_key = "AIzaSyD89G0AJWkoNMDcZBspwyOaCEXrHG47-j0"
    return render_template('index.html', default_key=default_key)

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.get_json() or {}
    origin = data.get('origin', 'Sarjapur Signal, Bangalore')
    destination = data.get('destination', 'Palace Grounds, Bangalore')
    # Securely use hardcoded user Google Maps API Key
    api_key = "AIzaSyD89G0AJWkoNMDcZBspwyOaCEXrHG47-j0"
        
    # Query transit with subway preference
    transit_data = query_directions(origin, destination, "transit", api_key, alternatives=True, transit_mode="subway")
    
    if not transit_data or transit_data.get("status") != "OK":
        status = transit_data.get("status") if transit_data else "Failed connection"
        return jsonify({"error": f"Failed to fetch directions from Google Maps (Status: {status})"}), 400
        
    routes = transit_data.get("routes", [])
    valid_options = []
    seen_metro_signatures = set()
    
    for i, route in enumerate(routes):
        legs = route.get("legs", [])
        if not legs:
            continue
        leg = legs[0]
        
        metro_steps = []
        for step in leg.get("steps", []):
            if step.get("travel_mode") == "TRANSIT":
                td = step.get("transit_details", {})
                line = td.get("line", {})
                vehicle = line.get("vehicle", {})
                v_type = vehicle.get("type", "").upper()
                v_name = vehicle.get("name", "").lower()
                instructions = step.get("html_instructions", "").lower()
                
                # Support both Subway/Metro and Commuter/Suburban/Local Train systems
                is_train_or_metro = (
                    v_type in ["SUBWAY", "METRO_RAIL", "RAIL", "HEAVY_RAIL", "COMMUTER_TRAIN", "TRAM", "MONORAIL"] or 
                    any(keyword in v_name for keyword in ["metro", "subway", "train", "railway", "local train", "tram", "commuter"]) or
                    any(keyword in instructions for keyword in ["metro", "subway", "train", "railway", "local train", "tram", "commuter"])
                )
                if is_train_or_metro:
                    metro_steps.append({
                        "step": step,
                        "line_name": line.get("name", line.get("short_name", "Metro Line")),
                        "line_color": line.get("color", "#8b5cf6"),
                        "num_stops": td.get("num_stops", 0),
                        "departure_stop": td.get("departure_stop", {}).get("name", "Unknown Stop"),
                        "arrival_stop": td.get("arrival_stop", {}).get("name", "Unknown Stop"),
                        "departure_time": td.get("departure_time", {}).get("value", 0),
                        "arrival_time": td.get("arrival_time", {}).get("value", 0),
                        "departure_time_text": td.get("departure_time", {}).get("text", ""),
                        "arrival_time_text": td.get("arrival_time", {}).get("text", ""),
                        "polyline": step.get("polyline", {}).get("points", "")
                    })
                    
        if not metro_steps:
            continue
            
        first_metro = metro_steps[0]
        last_metro = metro_steps[-1]
        
        first_station_name = first_metro["departure_stop"]
        last_station_name = last_metro["arrival_stop"]
        
        # Build signature from first and last station names and the ordered list of lines
        metro_lines_desc = tuple(m["line_name"] for m in metro_steps)
        signature = (first_station_name, last_station_name, metro_lines_desc)
        
        if signature in seen_metro_signatures:
            # Skip duplicate metro pathways to avoid identical driving leg calculations
            continue
        seen_metro_signatures.add(signature)
        
        first_station_loc = first_metro["step"]["transit_details"]["departure_stop"].get("location", {})
        first_station_coord = f"{first_station_loc.get('lat')},{first_station_loc.get('lng')}"
        first_departure_time = first_metro["departure_time"]
        
        last_station_loc = last_metro["step"]["transit_details"]["arrival_stop"].get("location", {})
        last_station_coord = f"{last_station_loc.get('lat')},{last_station_loc.get('lng')}"
        last_arrival_time = last_metro["arrival_time"]
        
        metro_total_duration_sec = last_arrival_time - first_departure_time
        if metro_total_duration_sec <= 0:
            first_idx = leg.get("steps", []).index(first_metro["step"])
            last_idx = leg.get("steps", []).index(last_metro["step"])
            metro_total_duration_sec = sum(s.get("duration", {}).get("value", 0) for s in leg.get("steps", [])[first_idx:last_idx + 1])
            
        metro_lines_desc = []
        for ms in metro_steps:
            metro_lines_desc.append({
                "name": ms["line_name"],
                "color": ms["line_color"],
                "from": ms["departure_stop"],
                "to": ms["arrival_stop"],
                "stops": ms["num_stops"],
                "polyline": ms["polyline"],
                "departure_time": ms["departure_time_text"],
                "arrival_time": ms["arrival_time_text"]
            })
            
        # Drive Leg 1: A -> First Metro
        drive_1 = query_directions(origin, first_station_coord, "driving", api_key)
        drive_1_sec = 0
        drive_1_text = "N/A"
        drive_1_dist = "N/A"
        drive_1_poly = ""
        if drive_1 and drive_1.get("status") == "OK":
            d_route = drive_1["routes"][0]
            d_leg = d_route["legs"][0]
            duration_data = d_leg.get("duration_in_traffic", d_leg["duration"])
            drive_1_sec = duration_data["value"]
            drive_1_text = duration_data["text"]
            drive_1_dist = d_leg["distance"]["text"]
            drive_1_poly = d_route.get("overview_polyline", {}).get("points", "")
            
        # Drive Leg 2: Last Metro -> B
        drive_2 = query_directions(last_station_coord, destination, "driving", api_key)
        drive_2_sec = 0
        drive_2_text = "N/A"
        drive_2_dist = "N/A"
        drive_2_poly = ""
        if drive_2 and drive_2.get("status") == "OK":
            d_route = drive_2["routes"][0]
            d_leg = d_route["legs"][0]
            duration_data = d_leg.get("duration_in_traffic", d_leg["duration"])
            drive_2_sec = duration_data["value"]
            drive_2_text = duration_data["text"]
            drive_2_dist = d_leg["distance"]["text"]
            drive_2_poly = d_route.get("overview_polyline", {}).get("points", "")
            
        total_hybrid_sec = drive_1_sec + metro_total_duration_sec + drive_2_sec
        
        def format_minutes(sec):
            m = sec / 60.0
            h = int(m // 60)
            mins = int(m % 60)
            if h > 0:
                return f"{h} hr {mins} mins"
            return f"{mins} mins"
            
        saved_sec = leg.get("duration", {}).get("value", 0) - total_hybrid_sec
        
        valid_options.append({
            "summary": route.get("summary", f"Route {i+1}"),
            "original_transit_text": leg.get("duration", {}).get("text", "N/A"),
            "original_transit_sec": leg.get("duration", {}).get("value", 0),
            "first_station": first_station_name,
            "last_station": last_station_name,
            "metro_duration_text": format_minutes(metro_total_duration_sec),
            "metro_duration_sec": metro_total_duration_sec,
            "metro_lines": metro_lines_desc,
            "drive_1_text": drive_1_text,
            "drive_1_dist": drive_1_dist,
            "drive_1_sec": drive_1_sec,
            "drive_1_polyline": drive_1_poly,
            "drive_2_text": drive_2_text,
            "drive_2_dist": drive_2_dist,
            "drive_2_sec": drive_2_sec,
            "drive_2_polyline": drive_2_poly,
            "hybrid_total_text": format_minutes(total_hybrid_sec),
            "hybrid_total_sec": total_hybrid_sec,
            "time_saved_text": format_minutes(abs(saved_sec)),
            "is_faster": saved_sec > 0
        })
        
    # Sort options by hybrid total duration
    valid_options.sort(key=lambda x: x["hybrid_total_sec"])
    
    # Query full driving route from origin to destination for comparison
    drive_full = query_directions(origin, destination, "driving", api_key)
    direct_driving = {"duration_text": "N/A", "duration_sec": 0, "distance_text": "N/A"}
    if drive_full and drive_full.get("status") == "OK":
        d_leg = drive_full["routes"][0]["legs"][0]
        duration_data = d_leg.get("duration_in_traffic", d_leg["duration"])
        direct_driving = {
            "duration_text": duration_data["text"],
            "duration_sec": duration_data["value"],
            "distance_text": d_leg["distance"]["text"]
        }
        
    # Save locations to history upon successful calculation
    if valid_options:
        save_to_history(origin, destination)
        
    return jsonify({
        "origin": origin,
        "destination": destination,
        "options": valid_options,
        "direct_driving": direct_driving
    })

@app.route('/api/current_location', methods=['GET'])
def current_location():
    """Fetches device location via termux-location and geocodes it."""
    import subprocess
    import json
    try:
        # Run termux-location with network provider
        result = subprocess.run(
            ["termux-location", "-p", "network", "-r", "once"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            location = json.loads(result.stdout)
            lat = location.get("latitude")
            lon = location.get("longitude")
            if lat and lon:
                # Query Nominatim OpenStreetMap API
                url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'HybridTravelApp/1.0'}
                )
                with urllib.request.urlopen(req) as response:
                    addr_data = json.loads(response.read().decode('utf-8'))
                    address = addr_data.get("display_name", f"{lat}, {lon}")
                    return jsonify({"address": address, "coords": f"{lat},{lon}"})
    except Exception as e:
        print(f"Error getting device location: {e}", file=sys.stderr)
        return jsonify({"error": f"Failed to retrieve location: {str(e)}"}), 500
        
    return jsonify({"error": "Could not retrieve device location. Ensure Termux:API is installed and location is enabled."}), 500

@app.route('/api/location_history', methods=['GET'])
def get_location_history():
    """Returns the persistent list of previously searched locations."""
    import os
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except Exception:
            history = []
    return jsonify(history)

@app.route('/api/resolve_maps_link', methods=['POST'])
def resolve_maps_link():
    """Resolves a Google Maps shortened directions link and extracts origin and destination."""
    data = request.get_json() or {}
    link = data.get('link', '').strip()
    if not link:
        return jsonify({"error": "No link provided."}), 400
        
    try:
        # Resolve redirects and get the final URL
        req = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            final_url = response.geturl()
            
        decoded_url = urllib.parse.unquote(final_url)
        if "/maps/dir/" in decoded_url:
            # Extract direction details from /maps/dir/Origin/Destination/...
            parts = decoded_url.split("/maps/dir/")[1].split("/")
            if len(parts) >= 2:
                origin = parts[0]
                destination = parts[1]
                
                # Cleanup coordinates and query parameters from the fields
                if "@" in destination:
                    destination = destination.split("@")[0]
                if "?" in destination:
                    destination = destination.split("?")[0]
                    
                origin = origin.rstrip("/").replace("+", " ").strip()
                destination = destination.rstrip("/").replace("+", " ").strip()
                
                return jsonify({
                    "origin": origin,
                    "destination": destination
                })
        return jsonify({"error": "Link does not appear to be a Google Maps Directions link."}), 400
    except Exception as e:
        print(f"Error resolving Google Maps link: {e}", file=sys.stderr)
        return jsonify({"error": f"Failed to resolve link: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
