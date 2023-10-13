from django.urls import path
from locations import views


# Endpoints for locations
urlpatterns = [
    path('api/get_static_map/', views.get_static_map),
    path('api/photos/', views.get_place_photo),
    path('api/places/', views.search_nearby_places),
    path('api/get_mapbox_token/', views.get_mapbox_token)
]