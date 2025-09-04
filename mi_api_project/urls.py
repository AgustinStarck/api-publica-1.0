"""
URL configuration for mi_api_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def home(request):
    return JsonResponse({
        'message': 'Bienvenido a la API de Noticias',
        'version': '1.0',
        'endpoints': {
            'noticias': '/api/noticias/',
            'noticias_con_filtro': '/api/noticias/?search=[término]&limit=[número]',
            'scheduler_status': '/api/scheduler-status/',
            'run_scraper': '/api/run-scraper/?limit=10',
            'control_scheduler': '/api/control-scheduler/ (POST con {"action": "start"|"stop"})',
            'admin': '/admin/'
        },
        'examples': {
            'todas_noticias': 'http://127.0.0.1:8080/api/noticias/',
            'buscar_tecnologia': 'http://127.0.0.1:8080/api/noticias/?search=tecnología',
            'limitar_5': 'http://127.0.0.1:8080/api/noticias/?limit=5',
            'ejecutar_scraper': 'http://127.0.0.1:8080/api/run-scraper/?limit=8'
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('mi_api_app.urls')),
    path('', home, name='home'),
]
