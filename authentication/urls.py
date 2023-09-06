from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('delete_user/', views.delete_user, name='delete_user'),
    path('profile/', views.profile_api, name='profile_api'),
    path('logout/', views.logout_view, name='logout')
]
