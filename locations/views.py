from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from json.decoder import JSONDecodeError
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from .serializers import LocationSerializer
from .models import Location

@api_view(['GET', 'POST'])
@csrf_exempt
def locations(request):

    if (request.method == 'GET'):
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif (request.method == 'POST'):
        try:
            data = JSONParser().parse(request)
            serializer = LocationSerializer(data=data)
        except JSONDecodeError as e:
            return JsonResponse({"error": "Invalid JSON data: " + str(e)}, status=400)

        if (serializer.is_valid()):
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
@csrf_exempt
def location_detail(request, pk):
    try:
        location = Location.objects.get(pk=pk)
    except Location.DoesNotExist:
        return HttpResponse(status=404)

    if (request.method == 'GET'):
        serializer = LocationSerializer(location)
        return JsonResponse(serializer.data)

    elif (request.method == 'PUT'):
        try:
            data = JSONParser().parse(request)
            serializer = LocationSerializer(location, data=data)
        except JSONDecodeError as e:
            return JsonResponse({"error": "Invalid JSON data: " + str(e)}, status=400)

        if (serializer.is_valid()):
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    elif (request.method == 'DELETE'):
        location.delete()
        return HttpResponse(status=204)
