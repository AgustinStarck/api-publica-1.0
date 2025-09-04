from django.urls import path
from mi_api_app import views_api

urlpatterns = [
    path('noticias/', views_api.get_noticias_json, name='get_noticias_json'),
    path('scheduler-status/', views_api.scheduler_status, name='scheduler_status'),
    path('run-scraper/', views_api.run_scraper_now, name='run_scraper_now'),
    path('control-scheduler/', views_api.control_scheduler, name='control_scheduler'),
]