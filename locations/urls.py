from django.urls import path
from locations import views

# define the urls
urlpatterns = [
    path('locations/', views.locations),
    path('locations/<int:pk>/', views.location_detail),
]
