import requests
import os
from django.http import HttpResponse
from authentication.views import is_authenticated


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