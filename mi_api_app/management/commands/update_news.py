# mi_api_app/management/commands/update_news.py
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Actualiza todas las noticias desde los feeds RSS'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=3, help='Límite de noticias por feed')

    def handle(self, *args, **options):
        self.stdout.write("🔄 Iniciando actualización de noticias...")
        
        # Ejecutar el comando de importación
        call_command('import_rss', limit=options['limit'])
        
        self.stdout.write(self.style.SUCCESS("✅ Actualización completada"))