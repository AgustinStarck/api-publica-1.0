# mi_api_app/__init__.py
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class MiApiAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mi_api_app'
    
    def ready(self):
        # Importar el startup para iniciar el scheduler
        try:
            from . import startup
            logger.info("✅ Scheduler de noticias iniciado")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo iniciar el scheduler: {e}")