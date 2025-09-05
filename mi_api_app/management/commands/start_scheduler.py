# mi_api_app/management/commands/start_scheduler.py
from django.core.management.base import BaseCommand
import threading
import time
import logging
from django.core.management import call_command

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Inicia el scheduler de noticias'
    
    def add_arguments(self, parser):
        parser.add_argument('--immediate', action='store_true', help='Ejecutar inmediatamente')
    
    def handle(self, *args, **options):
        def run_scheduler():
            """Función que corre en segundo plano"""
            logger.info("🔄 Scheduler iniciado (ejecutando cada 40 minutos)")
            
            if options['immediate']:
                try:
                    logger.info("🔄 Ejecutando scraper inmediatamente...")
                    call_command('import_rss', limit=30)
                    logger.info("✅ Scraper completado")
                except Exception as e:
                    logger.error(f"❌ Error en scraper: {e}")
            
            
            while True:
                time.sleep(780)  
                try:
                    logger.info("🔄 Ejecutando scraper automático...")
                    call_command('import_rss', limit=30)
                    logger.info("✅ Scraper automático completado")
                except Exception as e:
                    logger.error(f"❌ Error en scraper automático: {e}")
        
        # Iniciar el scheduler en un hilo
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        self.stdout.write(
            self.style.SUCCESS('✅ Scheduler iniciado en segundo plano')
        )
        self.stdout.write('⏰ Se ejecutará cada 40 minutos')
        
        # Mantener el comando activo
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write('\n⏹️ Scheduler detenido')
            