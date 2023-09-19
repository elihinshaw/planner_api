from django.urls import path
from locations import views

urlpatterns = [
    path('places/', views.get_places),
    path('routes/data/', views.get_direction_data),
]
