# mi_api_app/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import noticias
from django.db.models import Q

@api_view(['GET'])
@permission_classes([AllowAny])
def get_noticias_json(request):
    """
    Endpoint único que devuelve las noticias en formato JSON específico
    {
        "title": title,
        "description": description,
        "site_icon": site_icon,
        "link": link
    }
    """
    try:
        # Obtener parámetros de query opcionales
        limit = int(request.GET.get('limit', 50))
        search = request.GET.get('search', '')
        
        # Construir queryset base
        noticias_qs = noticias.objects.all().order_by('-fecha')
        
        # Aplicar filtro de búsqueda si existe
        if search:
            noticias_qs = noticias_qs.filter(
                Q(titulo__icontains=search) |
                Q(descripcion__icontains=search)
            )
        
        # Limitar resultados
        noticias_list = noticias_qs[:limit]
        
        # Formatear la respuesta en el formato específico
        response_data = []
        for noticia in noticias_list:
            response_data.append({
                "title": noticia.titulo,
                "description": noticia.descripcion,
                "site_icon": noticia.site_icon,
                "link": noticia.link
            })
        
        return Response(response_data)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )