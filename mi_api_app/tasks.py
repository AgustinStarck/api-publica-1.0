# mi_api_app/tasks.py
from django_q.tasks import schedule
from django_q.models import Schedule
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

def setup_periodic_tasks():
    """
    Configura las tareas periódicas al iniciar el servidor
    """
    # Verificar si la tarea ya existe
    if not Schedule.objects.filter(func='mi_api_app.tasks.run_news_scraper').exists():
        schedule(
            'mi_api_app.tasks.run_news_scraper',
            name='Scraper de Noticias cada 40 minutos',
            schedule_type=Schedule.MINUTES,
            minutes=40,
            repeats=-1,  # Se repite indefinidamente
            next_run=None  # Ejecutar inmediatamente al iniciar
        )
        logger.info("✅ Tarea periódica configurada: Scraper cada 40 minutos")

def run_news_scraper():
    """
    Función que ejecuta el scraper de noticias
    """
    try:
        logger.info("🔄 Iniciando scraper automático de noticias...")
        
        # Ejecutar el comando de importación
        from io import StringIO
        import sys
        from django.core.management import call_command
        
        # Capturar output para logging
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        
        call_command('import_rss', limit=5)
        
        output = mystdout.getvalue()
        sys.stdout = old_stdout
        
        logger.info(f"✅ Scraper completado. Output: {output}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en scraper automático: {str(e)}")
        return False