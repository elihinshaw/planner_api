from django.urls import path
from . import views


# Endpoints for authentication
urlpatterns = [
    path("api/signup/", views.create_user),
    path("api/login/", views.create_token),
]
