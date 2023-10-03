import os
import requests
from django.http import JsonResponse
from authentication.views import is_authenticated
from .geocoding import geocode, geocode_2

def distance_data(origin, destination):
    url = 'https://trueway-directions2.p.rapidapi.com/FindDrivingPath'

    querystring = {"origin": origin, "destination": destination}

    headers = {
        "X-RapidAPI-Key": os.environ.get("TRUEWAY_API_KEY"),
        "X-RapidAPI-Host": "trueway-directions2.p.rapidapi.com"
    }

    # Send a request to the API and parse the JSON response
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    # Check if the response contains route data
    if 'route' in data:
        # Extract duration in seconds and convert to hours, minutes, and seconds
        route_data = data['route']
        duration_seconds = int(route_data.get('duration', 0))
        hours = duration_seconds // 3600
        remaining_seconds = duration_seconds % 3600
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60

        result = {
            # Convert meters to miles
            'distance': round(route_data.get('distance', 0) * 0.000621371, 1),
            'duration': {
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds
            },
        }
        return JsonResponse(result)
    else:
        return JsonResponse({"error": "Failed to retrieve route data"}, status=500)

@is_authenticated
def get_direction_data(request):
    try:
        # Get origin and destination from the request
        origin = request.GET.get("origin")
        destination = request.GET.get("destination")

        # Geocode origin and destination to get their coordinates
        origin_coords = geocode(origin)
        destination_coords = geocode(destination)

        # Create dictionaries with origin and destination coordinates
        dest_lat_lon = {
            f"{destination_coords.get('lat')}, {destination_coords.get('lon')}"}
        origin_lat_lon = {
            f"{origin_coords.get('lat')}, {origin_coords.get('lon')}"}

        # Get driving directions data based on origin and destination coordinates
        directions_response = distance_data(origin_lat_lon, dest_lat_lon)

        return directions_response

    except Exception as e:
        # Handle any internal server errors
        return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)
