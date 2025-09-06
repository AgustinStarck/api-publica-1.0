# mi_api_app/apps.py
from django.apps import AppConfig

class MiApiAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mi_api_app'
    
    def ready(self):
        
        import mi_api_app.scheduler