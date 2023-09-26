from django.urls import path
from . import views

# Endpoints for facts
urlpatterns = [
    path('factoid/', views.factoid, name='factoid'),
]
