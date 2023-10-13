from django.urls import path
from . import views

# Endpoints for facts
urlpatterns = [
    path('api/factoid/', views.factoid),
]
