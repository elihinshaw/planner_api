import os
import requests
from django.http import JsonResponse
from .places_api_geocoded import address_to_coordinates


def search_nearby_places(request):
    address = request.GET.get('address')
    place_type = request.GET.get('type')
    api_key = os.environ.get("PLACES_API_KEY")

    if not api_key:
        return JsonResponse({'error': 'API key is missing'}, status=400)    

    latitude, longitude = address_to_coordinates(address, api_key)

    if latitude is not None and longitude is not None:
        endpoint = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
        params = {
            'location': f'{latitude},{longitude}',
            'radius': '1000',
            'type': place_type,
            'key': api_key,
        }

        results = []

        while True:
            response = requests.get(endpoint, params=params)

            if response.status_code == 200:
                data = response.json()
                results.extend(data.get('results', []))

                # Check if there is a next page of results  
                next_page_token = data.get('next_page_token')
                if not next_page_token or len(results) >= 10:
                    break

                # Add the next page token to the params to retrieve the next page of results
                params['pagetoken'] = next_page_token
            else:
                return JsonResponse({'error': 'Error while fetching nearby places'}, status=500)

        # Get the first 10 results' coordinates and return both results and coords
        first_10_results = results[:10]
        coords = [{'latitude': result['geometry']['location']['lat'], 'longitude': result['geometry']['location']['lng']} for result in first_10_results]

        response_data = {
            'results': first_10_results,
            'coords': coords
        }

        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Geocoding failed for the provided address'}, status=400)


def place_details(request):
    place_id = request.GET.get('place_id')
    api_key = os.environ.get("PLACES_API_KEY")

    if not api_key:
        return JsonResponse({'error': 'API key is missing'}, status=400)    


    endpoint = 'https://maps.googleapis.com/maps/api/place/details/json'
    params = {
        "place_id": place_id,
        'key': api_key,
    }

    while True:
        response = requests.get(endpoint, params=params)

        if response.status_code == 200:
            data = response.json()

        else:
            return JsonResponse({'error': 'Error while fetching nearby places'}, status=500)


        response_data = {
            'results': data,
        }

        return JsonResponse(response_data)