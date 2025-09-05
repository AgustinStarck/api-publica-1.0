from django.apps import AppConfig
import os
import logging

logger = logging.getLogger(__name__)

class MiApiAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mi_api_app'
    
    def ready(self):
        # Iniciar el scheduler cuando Django esté listo
        # En Render, siempre iniciar el scheduler
        if os.environ.get('RUN_MAIN') or os.environ.get('RENDER') or True:
            try:
                from .scheduler import start_scheduler
                start_scheduler()
                logger.info("✅ Scheduler de noticias iniciado automáticamente")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo iniciar el scheduler: {e}")