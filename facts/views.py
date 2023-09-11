from django.http import JsonResponse
import requests

def factoid(request):
    url = "https://uselessfacts.jsph.pl/api/v2/facts/random?language=en"

    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            fact = data.get("text")

            response_data = {
                "fact": fact
            }

            return JsonResponse(response_data)

        else:
            return JsonResponse({"error": "Failed to retrieve data"}, status=500)

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)
