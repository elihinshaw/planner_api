from django.urls import path
from . import views

# Endpoints for authentication
urlpatterns = [
    path("signup/", views.SignUp.as_view(), name="signup"),
    path("login/", views.CreateToken.as_view(), name="login"),
    path("hello/", views.SayHello.as_view(), name="hello"),
    ]
