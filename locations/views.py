from django.http import JsonResponse, HttpResponse
import requests
import time
import os
from authentication.views import is_authenticated


def geocode(address):
    try:
        if not address:  # Check if address is empty
            return {"error": "Address is required"}

        url = f"https://geocode.maps.co/search?q={address}"

        response = requests.get(url)  # Send a GET request to the API

        if response.status_code == 200:  # Check if the request was successful
            data = response.json()  # Parse the JSON response

            # Check if there are geocoding results
            if isinstance(data, list) and len(data) > 0:
                first_result = data[0]
                lat_str = first_result.get("lat")
                lon_str = first_result.get("lon")

                if lat_str is not None and lon_str is not None:  # Check if latitude and longitude are available
                    lat = float(lat_str)
                    lon = float(lon_str)
                    # Return the latitude and longitude
                    return {"lat": lat, "lon": lon}
                else:
                    # Error if lat or lon is missing
                    return {"error": "Latitude or longitude not found"}
            else:
                # Error if no results found
                return {"error": "No geocoding results found"}
        else:
            # Error for non-200 response
            return {"error": "Failed to retrieve data from geocoding service"}

    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        return {"error": f"Geocoding request failed: {str(e)}"}


def geocode_2(address):
    try:
        if not address:  # Check if address is empty
            return {"error": "Address is required"}

        url = "https://us1.locationiq.com/v1/search"

        data = {
            # Get API key from environment variable
            'key': os.environ.get("LOCATION_IQ_KEY"),
            'q': address,  # Set the query parameter
            'format': 'json'  # Request JSON format response
        }

        # Send a GET request with query parameters
        response = requests.get(url, params=data)

        if response.status_code == 200:  # Check if the request was successful
            json_data = response.json()  # Parse the JSON response

            # Check if there are geocoding results
            if isinstance(json_data, list) and len(json_data) > 0:
                first_result = json_data[1]
                lat_str = first_result.get("lat")
                lon_str = first_result.get("lon")

                if lat_str is not None and lon_str is not None:  # Check if latitude and longitude are available
                    lat = float(lat_str)
                    lon = float(lon_str)
                    # Return the latitude and longitude
                    return {"lat": lat, "lon": lon}
                else:
                    # Error if lat or lon is missing
                    return {"error": "Latitude or longitude not found"}
            else:
                # Error if no results found
                return {"error": "No geocoding results found"}
        else:
            # Error for non-200 response
            return {"error": "Failed to retrieve data from geocoding service"}

    except requests.exceptions.RequestException as e:
        # Handle request exceptions
        return {"error": f"Geocoding request failed: {str(e)}"}


def places_data(lat_lon_data, types):
    # Extract latitude and longitude from input data
    lat = lat_lon_data.get("lat")
    lon = lat_lon_data.get("lon")

    url = "https://trueway-places.p.rapidapi.com/FindPlacesNearby"

    # Define query parameters for the API request
    querystring = {
        "location": f"{lat},{lon}",
        "type": [types],
        "radius": "1000",
        "language": "en"
    }

    # Set headers with the API key and host
    headers = {
        "X-RapidAPI-Key": os.environ.get("TRUEWAY_API_KEY"),
        "X-RapidAPI-Host": "trueway-places.p.rapidapi.com",
    }

    try:
        # Send a GET request to the API
        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                return JsonResponse(data)
            else:
                return JsonResponse(data, safe=False)
        else:
            return JsonResponse({"error": "Failed to retrieve data from places service"}, status=500)

    except requests.exceptions.RequestException as e:
        # Handle any exceptions raised during the request
        return JsonResponse({"error": f"Places request failed: {str(e)}"}, status=500)


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
def get_static_map(request):

    origin = request.GET.get("origin")
    destination = request.GET.get("destination")
    # url of Map Quest API (API used for finding a static map in this case)
    url = "https://www.mapquestapi.com/staticmap/v5/map"

    querystring = {
        "start": origin,
        "end": destination,
        "size": "500,400@2x",
        "key": os.environ.get("MAP_QUEST_API_KEY"),
    }

    response = requests.get(url, params=querystring)

    if response.status_code == 200:
        # Get the content of the response as bytes
        image_data = response.content

        # Create an HTTP response with the image data
        return HttpResponse(image_data, content_type="image/png")
    else:
        # Handle the case when the API request fails
        return HttpResponse("Failed to fetch the image", status=500)


@is_authenticated
def get_places(request):
    try:
        # Get address and type param from the request
        address = request.GET.get("address")
        type_param = request.GET.get("type")

        # Handle type param, ensuring it's not an error
        if type_param is not None and "error" in type_param:
            type_param = None
        else:
            types = type_param.split(",") if type_param else []

        # Geocode the address
        geocode_result = geocode(address)

        # Handle geocoding errors
        if "error" in geocode_result:
            return JsonResponse(geocode_result, status=400)

        # Extract latitude and longitude from the geocoding result
        lat = geocode_result.get("lat")
        lon = geocode_result.get("lon")

        # Create a dictionary with latitude and longitude
        lat_lon_data = {"lat": lat, "lon": lon}

        # Get places data based on location and types
        places_response = places_data(lat_lon_data, types)
        places_json = places_response.content.decode('utf-8')

        # If no places found, retry using other geocoding API with a slight delay (to avoid rate limiting)
        if places_json == '{"results": []}':
            time.sleep(1)

            # Perform second geocoding
            geocode_2_result = geocode_2(address)

            # Handle geocoding errors for the second attempt
            if "error" in geocode_2_result:
                return JsonResponse(geocode_2_result, status=500)

            # Extract latitude and longitude from the second result
            lat = geocode_2_result.get("lat")
            lon = geocode_2_result.get("lon")

            # Update the latitude and longitude data
            lat_lon_data = {"lat": lat, "lon": lon}

            # Try to get places data again based on the updated location
            places_response = places_data(lat_lon_data, types)

        return places_response

    except Exception as e:
        # Handle any internal server errors
        return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)


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
