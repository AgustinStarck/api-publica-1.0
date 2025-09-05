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
        logger.info("✅ Scheduler iniciado (ejecutando cada 10 minutos)")
    
    def run_manual(self, limit=10, search='', category=''):
        """Ejecuta el scraper manualmente con filtros"""
        try:
            logger.info(f"🔄 Ejecutando scraper manual (limit: {limit}, search: '{search}', category: '{category}')...")
            
            # Construir comando con filtros
            command_args = ['import_rss', f'--limit={limit}']
            if search:
                command_args.append(f'--search={search}')
            if category:
                command_args.append(f'--category={category}')
            
            call_command(*command_args)
            logger.info("✅ Scraper manual completado")
            return True
        except Exception as e:
            logger.error(f"❌ Error en scraper manual: {e}")
            return False
    
    def _run_scheduler(self):
        """Loop principal del scheduler - se ejecuta AUTOMÁTICAMENTE cada 40 minutos"""
        logger.info("⏰ Scheduler automático iniciado")
        
        # Esperar 2 minutos para que Django esté completamente ready
        time.sleep(120)
        
        # Ejecutar inmediatamente al iniciar
        self._run_auto_scraper()
        
        # Luego ejecutar cada 40 minutos (2400 segundos)
        while self.is_running:
            try:
                # Esperar 40 minutos
                for i in range(700):
                    if not self.is_running:
                        break
                    time.sleep(1)
                
                if self.is_running:
                    self._run_auto_scraper()
                    
            except Exception as e:
                logger.error(f"❌ Error en scheduler automático: {e}")
                time.sleep(300)  # Esperar 5 minutos antes de reintentar
    
    def _run_auto_scraper(self):
        """Ejecuta el scraper automático con rotación de categorías"""
        try:
            # Rotar entre diferentes categorías en cada ejecución
            categories = ['tecnología', 'deportes', 'economía', 'ciencia', 'salud', 'política']
            current_category = categories[int(time.time() / 2400) % len(categories)]
            
            logger.info(f"🔄 Ejecutando scraper AUTOMÁTICO (categoría: {current_category})...")
            
            call_command('import_rss', limit=10, search=current_category)
            logger.info(f"✅ Scraper automático completado para {current_category}")
            
        except Exception as e:
            logger.error(f"❌ Error en scraper automático: {e}")
    
    def stop(self):
        """Detiene el scheduler"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("⏹️ Scheduler detenido")

# Instancia global del scheduler
scheduler = NewsScheduler()

def start_scheduler():
    """Función para iniciar el scheduler - ESTO ES LO QUE DEBES USAR"""
    scheduler.start()