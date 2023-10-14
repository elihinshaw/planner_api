import requests


def address_to_coordinates(address, api_key):
    geocoding_endpoint = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        'address': address,
        'key': api_key,
    }

    response = requests.get(geocoding_endpoint, params=params)

    if response.status_code == 200:
        data = response.json()
        location = data.get('results')[0]['geometry']['location']
        latitude = location['lat']
        longitude = location['lng']
        return latitude, longitude
    else:
        return None, None
