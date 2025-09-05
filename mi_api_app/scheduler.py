# mi_api_app/scheduler.py
import threading
import time
import logging
from django.core.management import call_command

logger = logging.getLogger(__name__)

def start_scheduler():
    """Inicia el scheduler de forma simple"""
    def run():
        logger.info("🔄 Scheduler iniciado (cada 13 minutos)")
        
        
        try:
            logger.info("🔄 Ejecutando scraper automático...")
            call_command('import_rss', limit=30)
            logger.info("✅ Scraper automático completado")
        except Exception as e:
            logger.error(f"❌ Error: {e}")
        
        
        while True:
            time.sleep(600)
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
    
    def run_manual(self, limit=10, search='', category=''):
        """Ejecuta el scraper manualmente con filtros"""
        try:
            logger.info(f"🔄 Ejecutando scraper manual (limit: {limit}, search: '{search}', category: '{category}')...")
            
            # Construir argumentos para el comando
            command_args = ['import_rss', f'--limit={limit}']
            
            if search:
                command_args.append(f'--search={search}')
            if category:
                command_args.append(f'--category={category}')
            
            # Ejecutar el comando
            call_command(*command_args)
            
            logger.info("✅ Scraper manual completado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en scraper manual: {str(e)}")
            return False

# Instancia global del scheduler
scheduler = NewsScheduler()

def start_scheduler():
    """Función para iniciar el scheduler"""
    scheduler.start()