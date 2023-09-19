from django.http import JsonResponse
import requests
import time
import os
from authentication.views import is_authenticated



def geocode(address):
    try:
        if not address:
            return {"error": "Address is required"}

        url = f"https://geocode.maps.co/search?q={address}"

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            if isinstance(data, list) and len(data) > 0:
                first_result = data[0]
                lat_str = first_result.get("lat")
                lon_str = first_result.get("lon")

                if lat_str is not None and lon_str is not None:
                    lat = float(lat_str)
                    lon = float(lon_str)
                    return {"lat": lat, "lon": lon}
                else:
                    return {"error": "Latitude or longitude not found"}
            else:
                return {"error": "No geocoding results found"}
        else:
            return {"error": "Failed to retrieve data from geocoding service"}

    except requests.exceptions.RequestException as e:
        return {"error": f"Geocoding request failed: {str(e)}"}


def geocode_2(address):
    try:
        if not address:
            return {"error": "Address is required"}

        url = "https://us1.locationiq.com/v1/search"

        data = {
            'key': os.environ.get("LOCATION_IQ_KEY"),
            'q': address,
            'format': 'json'
        }

        response = requests.get(url, params=data)

        if response.status_code == 200:
            json_data = response.json()

            if isinstance(json_data, list) and len(json_data) > 0:
                first_result = json_data[1]
                lat_str = first_result.get("lat")
                lon_str = first_result.get("lon")

                if lat_str is not None and lon_str is not None:
                    lat = float(lat_str)
                    lon = float(lon_str)
                    return {"lat": lat, "lon": lon}
                else:
                    return {"error": "Latitude or longitude not found"}
            else:
                return {"error": "No geocoding results found"}
        else:
            return {"error": "Failed to retrieve data from geocoding service"}

    except requests.exceptions.RequestException as e:
        return {"error": f"Geocoding request failed: {str(e)}"}


def places_data(lat_lon_data, types):
    lat = lat_lon_data.get("lat")
    lon = lat_lon_data.get("lon")

    url = "https://trueway-places.p.rapidapi.com/FindPlacesNearby"

    querystring = {
        "location": f"{lat},{lon}",
        "type": [types],
        "radius": "1000",
        "language": "en"
    }

    headers = {
        "X-RapidAPI-Key": os.environ.get("TRUEWAY_API_KEY"),
        "X-RapidAPI-Host": "trueway-places.p.rapidapi.com",
    }

    try:
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
        return JsonResponse({"error": f"Places request failed: {str(e)}"}, status=500)

def distance_data(origin, destination):

    url = 'https://trueway-directions2.p.rapidapi.com/FindDrivingPath'

    querystring = {"origin":origin,"destination":destination}

    headers = {
	"X-RapidAPI-Key": os.environ.get("TRUEWAY_API_KEY"),
	"X-RapidAPI-Host": "trueway-directions2.p.rapidapi.com"
}
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    if 'route' in data:
        route_data = data['route']
        duration_seconds = int(route_data.get('duration', 0))

        duration_minutes = duration_seconds // 60
        remaining_seconds = duration_seconds % 60

        duration_formatted = f"Estimated {duration_minutes} minutes and {remaining_seconds} seconds"

        result = {
            'distance': f"Estimated {round(route_data.get('distance', 0) * 0.000621371, 1)} miles",
            'duration': duration_formatted
        }
        return JsonResponse(result)
    else:
        return JsonResponse({"error": "Failed to retrieve route data"}, status=500)


@is_authenticated
def get_places(request):
    try:
        address = request.GET.get("address")
        type_param = request.GET.get("type")

        if type_param is not None and "error" in type_param:
            type_param = None
        else:
            types = type_param.split(",") if type_param else []

        geocode_result = geocode(address)

        if "error" in geocode_result:
            return JsonResponse(geocode_result, status=400)

        lat = geocode_result.get("lat")
        lon = geocode_result.get("lon")

        lat_lon_data = {"lat": lat, "lon": lon}

        places_response = places_data(lat_lon_data, types)
        places_json = places_response.content.decode('utf-8')

        if places_json == '{"results": []}':
            time.sleep(1)

            geocode_2_result = geocode_2(address)

            if "error" in geocode_2_result:
                return JsonResponse(geocode_2_result, status=500)

            lat = geocode_2_result.get("lat")
            lon = geocode_2_result.get("lon")

            lat_lon_data = {"lat": lat, "lon": lon}

            places_response = places_data(lat_lon_data, types)

        return places_response

    except Exception as e:
        return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)

@is_authenticated
def get_direction_data(request):
    try:
        origin = request.GET.get("origin")
        destination = request.GET.get("destination")

        origin_coords = geocode(origin)
        destination_coords = geocode(destination)

        dest_lat_lon = {f"{destination_coords.get('lat')}, {destination_coords.get('lon')}" }
        origin_lat_lon = {f"{origin_coords.get('lat')}, {origin_coords.get('lon')}" }

        directions_response = distance_data(origin_lat_lon, dest_lat_lon)

        return directions_response

    except Exception as e:
        return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)
