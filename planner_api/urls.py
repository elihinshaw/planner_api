from django.urls import path, include

urlpatterns = [
    path('', include('locations.urls')),
    path('', include('authentication.urls')),
    path('', include('facts.urls')),
]
