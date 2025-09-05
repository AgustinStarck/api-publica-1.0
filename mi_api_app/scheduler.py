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
        """Inicia el scheduler automáticamente"""
        if self.is_running:
            logger.warning("⚠️ El scheduler ya está ejecutándose")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("✅ Scheduler iniciado (ejecutando cada 40 minutos)")
    
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
    
    def _run_scheduler(self):
        """Loop principal del scheduler - se ejecuta AUTOMÁTICAMENTE"""
        logger.info("⏰ Scheduler iniciado - Primera ejecución en 1 minuto...")
        
        # Esperar 1 minuto para que Django esté completamente ready
        time.sleep(60)
        
        while self.is_running:
            try:
                logger.info("🔄 Ejecutando scraper AUTOMÁTICO...")
                call_command('import_rss', limit=10)
                logger.info("✅ Scraper automático completado")
                
               
                for i in range(10):
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"❌ Error en scheduler automático: {e}")
                time.sleep(300)  # Esperar 5 minutos antes de reintentar
    
    def _run_scraper(self):
        """Función auxiliar para ejecutar el scraper"""
        try:
            call_command('import_rss', limit=30)
        except Exception as e:
            logger.error(f"❌ Error en scraper: {e}")

# Instancia global del scheduler
scheduler = NewsScheduler()

def start_scheduler():
    """Función para iniciar el scheduler"""
    scheduler.start()