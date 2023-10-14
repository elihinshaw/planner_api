from django.urls import path, include


# Importing all the urls from each app, then using them here
urlpatterns = [
    path('', include('locations.urls')),
    path('', include('authentication.urls')),
    path('', include('facts.urls')),
]
