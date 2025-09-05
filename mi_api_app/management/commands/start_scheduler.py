from django.core.management.base import BaseCommand
from mi_api_app.scheduler import start_scheduler
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Inicia el scheduler automático de noticias manualmente'
    
    def add_arguments(self, parser):
        parser.add_argument('--immediate', action='store_true', help='Ejecutar scraper inmediatamente')
        parser.add_argument('--interval', type=int, default=10, help='Intervalo en minutos (default: 10)')
    
    def handle(self, *args, **options):
        immediate = options['immediate']
        interval = options['interval']
        
        self.stdout.write("🚀 Iniciando scheduler de noticias...")
        self.stdout.write(f"⏰ Intervalo: {interval} minutos")
        self.stdout.write(f"🎯 Ejecución inmediata: {'Sí' if immediate else 'No'}")
        
        try:
            # Importar e iniciar el scheduler
            from mi_api_app.scheduler import scheduler
            
            if scheduler.is_running:
                self.stdout.write(
                    self.style.WARNING("⚠️ El scheduler ya está ejecutándose")
                )
                return
            
            # Iniciar el scheduler
            start_scheduler()
            
            # Ejecutar inmediatamente si se solicita
            if immediate:
                self.stdout.write("🔄 Ejecutando scraper inmediatamente...")
                try:
                    from django.core.management import call_command
                    call_command('import_rss', limit=20)
                    self.stdout.write("✅ Scraper inmediato completado")
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Error en scraper inmediato: {e}")
                    )
            
            self.stdout.write(
                self.style.SUCCESS('✅ Scheduler iniciado correctamente')
            )
            self.stdout.write(f'⏰ Se ejecutará automáticamente cada {interval} minutos')
            self.stdout.write('📊 Para ver logs: Revisa la consola de Render')
            self.stdout.write('⏹️ Para detener: Reinicia el servicio en Render')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al iniciar scheduler: {e}')
            )
            logger.error(f"Error iniciando scheduler: {e}")