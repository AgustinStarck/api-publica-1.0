import feedparser
import re
import json
import html
import unicodedata
from urllib.parse import urlparse
import time
import logging

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Eliminar HTML
    text = re.sub(r"<.*?>", "", text)
    # Decodificar entidades HTML (&amp; → &)
    text = html.unescape(text)
    # Normalizar caracteres raros
    text = unicodedata.normalize("NFKC", text)
    # Quitar espacios extra
    return text.strip()

def extract_image_url(entry):
    """Extrae la URL de la imagen de una entrada RSS usando múltiples métodos"""
    image_url = None
    
    # 1. Buscar en media_content (elementos media con type image/* o medium=image)
    if hasattr(entry, 'media_content'):
        for media in entry.media_content:
            media_type = media.get('type', '').lower()
            medium = media.get('medium', '').lower()
            if (media_type.startswith('image/') or medium == 'image'):
                image_url = media.get('url', '')
                if image_url:
                    return image_url
    
    # 2. Buscar específicamente en elementos media:content (namespace media)
    # Estos a menudo se almacenan en campos con namespace como entry['media_content']
    if hasattr(entry, 'media_content') or 'media_content' in entry:
        media_content = entry.get('media_content', [])
        for media in media_content:
            # Verificar si es un diccionario con los atributos esperados
            if isinstance(media, dict):
                media_type = media.get('type', '').lower()
                medium = media.get('medium', '').lower()
                if (media_type.startswith('image/') or medium == 'image'):
                    image_url = media.get('url', '')
                    if image_url:
                        return image_url
    
    # 3. Buscar en media_thumbnail
    if hasattr(entry, 'media_thumbnail'):
        for thumbnail in entry.media_thumbnail:
            image_url = thumbnail.get('url', '')
            if image_url:
                return image_url
    
    # 4. Buscar en enclosures (con type image/*)
    if hasattr(entry, 'enclosures'):
        for enclosure in entry.enclosures:
            enclosure_type = enclosure.get('type', '').lower()
            if enclosure_type.startswith('image/'):
                image_url = enclosure.get('href', '')
                if image_url:
                    return image_url
    
    # 5. Buscar en links (con type image/* o rel='image')
    if hasattr(entry, 'links'):
        for link_item in entry.links:
            link_type = link_item.get('type', '').lower()
            link_rel = link_item.get('rel', '').lower()
            if (link_type.startswith('image/') or link_rel == 'image' or 
                'image' in link_rel or 'thumbnail' in link_rel):
                image_url = link_item.get('href', '')
                if image_url:
                    return image_url
    
    # 6. Buscar en namespaces específicos (como media:content en el namespace Yahoo)
    # Alimentadores como Yahoo News usan este formato
    for key in entry.keys():
        if 'media' in key.lower() or 'thumbnail' in key.lower():
            value = entry[key]
            # Si es una lista, buscar elementos con URL
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and 'url' in item:
                        image_url = item['url']
                        if image_url and any(ext in image_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                            return image_url
            # Si es un diccionario, extraer la URL directamente
            elif isinstance(value, dict) and 'url' in value:
                image_url = value['url']
                if image_url and any(ext in image_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    return image_url
            # Si es una cadena que parece una URL de imagen
            elif isinstance(value, str) and value.startswith(('http://', 'https://')):
                if any(ext in value.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    return value
    
    # 7. Buscar campos específicos comunes en diferentes feeds
    image_fields = [
        'media:content', 'media:thumbnail', 'image', 'thumbnail',
        'featured_image', 'enclosure', 'content_image', 'url'
    ]
    
    for field in image_fields:
        if field in entry:
            field_value = entry[field]
            if isinstance(field_value, str) and field_value.startswith(('http://', 'https://')):
                if any(ext in field_value.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    return field_value
            elif isinstance(field_value, dict) and 'url' in field_value:
                image_url = field_value['url']
                if image_url and any(ext in image_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    return image_url
            elif isinstance(field_value, list):
                for item in field_value:
                    if isinstance(item, dict) and 'url' in item:
                        image_url = item['url']
                        if image_url and any(ext in image_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                            return image_url
    
    # 8. Buscar en el contenido HTML usando expresiones regulares
    content_sources = []
    
    # Agregar posibles fuentes de contenido HTML
    if hasattr(entry, 'content'):
        for content in entry.content:
            content_value = content.get('value', '')
            if content_value:
                content_sources.append(content_value)
    
    # Añadir otras fuentes potenciales de contenido HTML
    potential_content_fields = ['summary', 'description', 'content:encoded', 'media:description']
    for field in potential_content_fields:
        if field in entry:
            content_value = entry[field]
            if content_value:
                content_sources.append(content_value)
    
    # Patrones regex para encontrar URLs de imágenes
    img_patterns = [
        r'<img[^>]+src="([^">]+)"',  # Etiqueta img con src
        r'<img[^>]+srcset="[^"]*?\b([^">]+?\.(?:jpg|jpeg|png|gif|webp)[^">]*?)[,\s]"',  # srcset
        r'background-image:\s*url\([\'"]?([^\'"\)]+)[\'"]?\)',  # CSS background-image
        r'data-image="([^">]+)"',  # Atributos data específicos
        r'data-src="([^">]+)"',    # Lazy loading images
        r'data-lazy-src="([^">]+)"',  # Lazy loading específico
        r'<media:content[^>]+url="([^">]+)"',  # Elementos media:content con URL
        r'<media:thumbnail[^>]+url="([^">]+)"'  # Elementos media:thumbnail con URL
    ]
    
    for content in content_sources:
        if not content:
            continue
            
        for pattern in img_patterns:
            images = re.findall(pattern, content, re.IGNORECASE)
            for img_url in images:
                # Filtrar URLs de imágenes comunes (no placeholders ni iconos)
                if (img_url and 
                    any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']) and
                    not any(ignore in img_url.lower() for ignore in ['pixel', 'placeholder', 'icon', 'logo', 'spacer', 'avatar'])):
                    return img_url
    
    # 9. Buscar en metadatos extendidos (namespaces)
    if hasattr(entry, 'media_group'):
        for media in getattr(entry.media_group, 'media_content', []):
            if (hasattr(media, 'type') and media.type.startswith('image/') or
                hasattr(media, 'medium') and media.medium == 'image'):
                image_url = getattr(media, 'url', '')
                if image_url:
                    return image_url
    
    # 10. Buscar en campos personalizados que puedan contener URLs de imágenes
    custom_fields = [key for key in entry.keys() if any(term in key.lower() for term in 
                     ['image', 'img', 'thumb', 'photo', 'pic', 'media', 'url'])]
    
    for field in custom_fields:
        field_value = entry[field]
        if isinstance(field_value, str) and field_value.startswith(('http://', 'https://')):
            # Verificar si parece una URL de imagen
            if any(ext in field_value.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                return field_value
        elif isinstance(field_value, list) and field_value:
            # Si es una lista, tomar el primer elemento que parezca una URL de imagen
            for item in field_value:
                if (isinstance(item, str) and item.startswith(('http://', 'https://')) and
                    any(ext in item.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])):
                    return item
        elif isinstance(field_value, dict):
            # Si es un diccionario, buscar una clave 'url'
            if 'url' in field_value:
                url_value = field_value['url']
                if (isinstance(url_value, str) and url_value.startswith(('http://', 'https://')) and
                    any(ext in url_value.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])):
                    return url_value
    
    return None

def get_news_feed(url, limit: int = 1000):
    try:
        # Pequeña pausa para no saturar los servidores
        time.sleep(0.5)
        
        feed = feedparser.parse(url)
        news_list = []

        if hasattr(feed, 'bozo') and feed.bozo:
            logger.warning(f"Feed con errores: {url} - {feed.bozo_exception}")

        for entry in feed.entries[:limit]:
            try:
                title = clean_text(entry.get('title', 'Sin título'))
                description = clean_text(entry.get("summary", entry.get("description", "")))
                link = entry.get("link", "")
                
                if not link:
                    continue
                
                # Obtener dominio para el icono
                parsed_url = urlparse(link)
                domain = parsed_url.netloc
                site_icon = f"https://logo.clearbit.com/{domain}"

                # Extraer URL de la imagen usando la función mejorada
                image_url = extract_image_url(entry)

                news_item = {
                    "title": title[:199],  # Asegurar que no exceda el límite del modelo
                    "description": description[:1000],  # Limitar descripción
                    "site_icon": site_icon,
                    "link": link,
                    "image": image_url  # Agregar la URL de la imagen
                }
                news_list.append(news_item)
                
            except Exception as e:
                logger.error(f"Error procesando entrada en {url}: {e}")
                continue

        return json.dumps(news_list, indent=4, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Error procesando feed {url}: {e}")
        return json.dumps([], ensure_ascii=False)