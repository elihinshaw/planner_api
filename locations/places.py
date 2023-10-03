import os
import time
import requests
from django.http import JsonResponse
from .geocoding import geocode, geocode_2


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