# mi_api_app/scheduler.py
import threading
import time
import logging
from django.core.management import call_command
from django.conf import settings

logger = logging.getLogger(__name__)

class NewsScheduler:
    def __init__(self):
        self.is_running = False
        self.thread = None
    
    def start(self):
        """Inicia el scheduler en un hilo separado"""
        if self.is_running:
            logger.warning("⚠️ El scheduler ya está ejecutándose")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("✅ Scheduler iniciado (cada 40 minutos)")
    
    def stop(self):
        """Detiene el scheduler"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("⏹️ Scheduler detenido")
    
    def _run_scheduler(self):
        """Loop principal del scheduler"""
        while self.is_running:
            try:
                # Ejecutar el scraper inmediatamente al iniciar
                self._run_scraper()
                
                # Esperar 40 minutos (2400 segundos)
                for _ in range(2400):
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"❌ Error en scheduler: {e}")
                time.sleep(60)  # Esperar 1 minuto antes de reintentar
    
    def _run_scraper(self):
        """Ejecuta el comando de scraping"""
        try:
            logger.info("🔄 Ejecutando scraper automático...")
            call_command('import_rss', limit=10)
            logger.info("✅ Scraper automático completado")
        except Exception as e:
            logger.error(f"❌ Error en scraper automático: {e}")
    
    def run_manual(self, limit=10):
        """Ejecuta el scraper manualmente"""
        try:
            logger.info(f"🔄 Ejecutando scraper manual (limit: {limit})...")
            call_command('import_rss', limit=limit)
            logger.info("✅ Scraper manual completado")
            return True
        except Exception as e:
            logger.error(f"❌ Error en scraper manual: {e}")
            return False

# Instancia global del scheduler
scheduler = NewsScheduler()

def start_scheduler():
    """Función para iniciar el scheduler"""
    scheduler.start()

def stop_scheduler():
    """Función para detener el scheduler"""
    scheduler.stop()