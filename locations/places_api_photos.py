import os
import requests
from django.http import HttpResponse, JsonResponse


def get_place_photo(request):
    # Get the photo_reference from the query parameters
    photo_reference = request.GET.get("reference")

    # Ensure that a photo reference is provided
    if not photo_reference:
        return JsonResponse({"error": "No photo reference provided"})

    # Construct the URL for the photo request
    photo_url = f'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={os.environ.get("PLACES_API_KEY")}'

    try:
        # Send a request to the Google Places API to fetch the photo
        response = requests.get(photo_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Return the image data directly as a binary HTTP response
            return HttpResponse(response.content, content_type="image/jpeg")

        # Handle other status codes or errors
        else:
            return JsonResponse({"error": "Error fetching photo"}, status=response.status_code)

    except Exception as e:
        return JsonResponse({"error": str(e)})
