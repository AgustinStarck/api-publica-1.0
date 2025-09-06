import threading
import time
import logging
from django.core.management import call_command

logger = logging.getLogger(__name__)

def run_scheduler():
    """Función simple que corre en segundo plano"""
    logger.info("🔄 Scheduler iniciado (ejecutando cada 40 minutos)")
    
    
    time.sleep(5)
    
    
    try:
        logger.info("🔄 Ejecutando scraper automático...")
        call_command('import_rss', limit=5)
        logger.info("✅ Scraper automático completado")
    except Exception as e:
        logger.error(f"❌ Error en scraper automático: {e}")
    
    
    while True:
        time.sleep(2400)  
        try:
            logger.info("🔄 Ejecutando scraper automático...")
            call_command('import_rss', limit=5)
            logger.info("✅ Scraper automático completado")
        except Exception as e:
            logger.error(f"❌ Error en scraper automático: {e}")


scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()