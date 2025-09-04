# mi_api_app/scheduler.py
import threading
import time
import logging
from django.core.management import call_command

logger = logging.getLogger(__name__)

def start_scheduler():
    """Inicia el scheduler de forma simple"""
    def run():
        logger.info("🔄 Scheduler iniciado (cada 40 minutos)")
        
        # Ejecutar inmediatamente
        try:
            logger.info("🔄 Ejecutando scraper automático...")
            call_command('import_rss', limit=30)
            logger.info("✅ Scraper automático completado")
        except Exception as e:
            logger.error(f"❌ Error: {e}")
        
        # Luego cada 40 minutos
        while True:
            time.sleep(2400)
            try:
                logger.info("🔄 Ejecutando scraper automático...")
                call_command('import_rss', limit=5)
                logger.info("✅ Scraper automático completado")
            except Exception as e:
                logger.error(f"❌ Error: {e}")
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread

# Iniciar automáticamente al importar
scheduler_thread = start_scheduler()