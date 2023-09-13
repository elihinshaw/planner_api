from django.urls import path
from locations import views

# define the urls
urlpatterns = [
    path('places/', views.get_places),
]
