from django.urls import path
from . import views

urlpatterns = [
    path('factoid/', views.factoid, name='factoid'),
]
