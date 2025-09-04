from django.urls import path
from mi_api_app import views_api

urlpatterns = [
    path('noticias/', views_api.get_noticias_json, name='get_noticias_json'),
]