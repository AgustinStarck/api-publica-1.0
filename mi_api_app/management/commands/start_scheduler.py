# mi_api_app/scheduler.py
import threading
import time
import logging
from django.core.management import call_command

logger = logging.getLogger(__name__)

class NewsScheduler:
    def __init__(self):
        self.is_running = False
        self.thread = None
    
    def start(self):
        """Inicia el scheduler"""
        if self.is_running:
            return
        self.is_running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("✅ Scheduler iniciado")
    
    def run_manual(self, limit=30):  # ← ¡ESTE MÉTODO DEBE EXISTIR!
        """Ejecuta el scraper manualmente"""
        try:
            logger.info(f"🔄 Ejecutando scraper manual (limit: {limit})...")
            call_command('import_rss', limit=limit)
            logger.info("✅ Scraper manual completado")
            return True
        except Exception as e:
            logger.error(f"❌ Error en scraper manual: {e}")
            return False
    
    def _run_scheduler(self):
        """Loop principal del scheduler"""
        while self.is_running:
            try:
                self._run_scraper()
                time.sleep(720)  # 40 minutos
            except Exception as e:
                logger.error(f"❌ Error en scheduler: {e}")
                time.sleep(60)
    
    def _run_scraper(self):
        """Ejecuta el scraper automático"""
        try:
            logger.info("🔄 Ejecutando scraper automático...")
            call_command('import_rss', limit=30)
            logger.info("✅ Scraper automático completado")
        except Exception as e:
            logger.error(f"❌ Error en scraper automático: {e}")

# 👇 Asegurar que la instancia se crea correctamente
scheduler = NewsScheduler()

def start_scheduler():
    """Función para iniciar el scheduler"""
    scheduler.start()