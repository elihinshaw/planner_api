from django.urls import path
from locations import views

# Endpoints for locations
urlpatterns = [
    path('places/', views.get_places),
    path('routes/data/', views.get_direction_data),
    path('routes/map/', views.get_static_map),
    path('photos/', views.get_place_photo),
    path('places/api/places/', views.search_nearby_places)
]
