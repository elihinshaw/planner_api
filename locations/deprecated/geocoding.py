import requests
import os


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