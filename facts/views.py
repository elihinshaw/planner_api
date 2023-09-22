from django.http import JsonResponse
import requests


def factoid(request):
    url = "https://uselessfacts.jsph.pl/api/v2/facts/random?language=en"

    try:
        response = requests.get(url) # Send GET request to API

        if response.status_code == 200: # Check if response status code is OK

            data = response.json() # Parse the response

            fact = data.get("text") # Extract the fact from response

            # Create a response with the fact
            response_data = {
                "fact": fact
            }

            return JsonResponse(response_data) # Return fact as JSON

        else:
            # If the request to the API fails, ERROR (lol)
            return JsonResponse({"error": "Failed to retrieve data"}, status=500)

    except requests.exceptions.RequestException as e:
        # Handle other exceptions that may occur
        return JsonResponse({"error": str(e)}, status=500)
