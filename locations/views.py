from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .serializers import LocationSerializer
from .models import Location
import json

@csrf_exempt
def locations(request):
    if request.method == 'GET':
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            serializer = LocationSerializer(data=data)
        except json.JSONDecodeError as e:
            return HttpResponseBadRequest(f"Invalid JSON data: {str(e)}")

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

@csrf_exempt
def location_detail(request, pk):
    try:
        location = Location.objects.get(pk=pk)
    except Location.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = LocationSerializer(location)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body.decode('utf-8'))
            serializer = LocationSerializer(location, data=data)
        except json.JSONDecodeError as e:
            return HttpResponseBadRequest(f"Invalid JSON data: {str(e)}")

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        location.delete()
        return HttpResponse(status=204)
