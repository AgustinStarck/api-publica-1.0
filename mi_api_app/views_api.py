# mi_api_app/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import noticias
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

# Importamos el scheduler dentro de las funciones para evitar circular imports
def get_scheduler():
    from .scheduler import scheduler, start_scheduler
    
    # Si el scheduler no está corriendo, iniciarlo
    if not scheduler.is_running:
        start_scheduler()
    
    return scheduler

@api_view(['GET'])
@permission_classes([AllowAny])
def get_noticias_json(request):
    """Endpoint principal para obtener noticias"""
    try:
        limit = int(request.GET.get('limit', 50))
        search = request.GET.get('search', '')
        all_data = request.GET.get('all', '').lower() == 'true'
        
        noticias_qs = noticias.objects.all().order_by('-fecha')
        
        if search:
            noticias_qs = noticias_qs.filter(
                Q(titulo__icontains=search) |
                Q(descripcion__icontains=search)
            )
        
        # Si se piden todos los datos, ignorar el límite
        if all_data:
            noticias_list = list(noticias_qs)
        else:
            noticias_list = noticias_qs[:limit]
        
        response_data = []
        for noticia in noticias_list:
            response_data.append({
                "title": noticia.titulo,
                "description": noticia.descripcion,
                "site_icon": noticia.site_icon,
                "link": noticia.link,
                "image": noticia.image,
            })
        
        return Response(response_data)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def scheduler_status(request):
    """Estado del scheduler"""
    scheduler = get_scheduler()
    return Response({
        'status': 'active' if scheduler.is_running else 'inactive',
        'interval': 'cada 40 minutos',
        'is_running': scheduler.is_running,
        'message': 'El scraper se ejecuta automáticamente cada 40 minutos'
    })

@api_view(['GET', 'POST'])
def run_scraper_now(request):
    """Ejecutar scraper manualmente"""
    try:
        if request.method == 'GET':
            limit = int(request.GET.get('limit', 10))
        else:
            limit = int(request.data.get('limit', 10))
        
        scheduler = get_scheduler()  # ← Ahora devuelve la instancia
        
        # Verificar que el método existe
        if hasattr(scheduler, 'run_manual'):
            success = scheduler.run_manual(limit=limit)
            return Response({
                'success': success,
                'message': f'Scraper ejecutado con límite {limit}',
                'limit': limit
            })
        else:
            # Fallback al comando directo
            from django.core.management import call_command
            call_command('import_rss', limit=limit)
            return Response({
                'success': True,
                'message': f'Scraper ejecutado via comando (limit: {limit})'
            })
            
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        })

@api_view(['POST'])
def control_scheduler(request):
    """Controlar el scheduler (start/stop)"""
    scheduler = get_scheduler()
    action = request.data.get('action', '').lower()
    
    if action == 'start':
        scheduler.start()
        return Response({'status': 'started', 'message': 'Scheduler iniciado'})
    elif action == 'stop':
        scheduler.stop()
        return Response({'status': 'stopped', 'message': 'Scheduler detenido'})
    else:
        return Response({
            'error': 'Acción no válida. Use "start" o "stop"'
        }, status=400)
    