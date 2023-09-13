from django.http import JsonResponse
import requests
import time
import os

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

def places_data(lat_lon_data):
    lat = lat_lon_data.get("lat")
    lon = lat_lon_data.get("lon")

    url = "https://trueway-places.p.rapidapi.com/FindPlacesNearby"

    querystring = {
        "location": f"{lat},{lon}",
        "radius": "180",
        "language": "en"
    }

    headers = {
        "X-RapidAPI-Key": os.environ.get("TRUEWAY_PLACES_KEY"),
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


def get_places(request):
    try:
        address = request.GET.get("address")
        geocode_result = geocode(address)

        if "error" in geocode_result:
            return JsonResponse(geocode_result, status=400)

        lat = geocode_result.get("lat")
        lon = geocode_result.get("lon")

        lat_lon_data = {"lat": lat, "lon": lon}

        places_result = places_data(lat_lon_data)

        return places_result
    except Exception as e:
        return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)

def get_places(request):
    try:
        address = request.GET.get("address")
        geocode_result = geocode(address)

        if "error" in geocode_result:
            return JsonResponse(geocode_result, status=400)

        lat = geocode_result.get("lat")
        lon = geocode_result.get("lon")

        lat_lon_data = {"lat": lat, "lon": lon}

        places_response = places_data(lat_lon_data)
        places_json = places_response.content.decode('utf-8')

        if places_json == '{"results": []}':
            time.sleep(1)

            geocode_2_result = geocode_2(address)

            if "error" in geocode_2_result:
                return JsonResponse(geocode_2_result, status=500)

            lat = geocode_2_result.get("lat")
            lon = geocode_2_result.get("lon")

            lat_lon_data = {"lat": lat, "lon": lon}

            places_response = places_data(lat_lon_data)

        return places_response

    except Exception as e:
        return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)


