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

                # Buscar imágenes en la entrada
                image_url = None
                
                # Verificar si hay elementos media con type image/jpeg o image/png
                if hasattr(entry, 'media_content'):
                    for media in entry.media_content:
                        if media.get('type', '').startswith('image/'):
                            image_url = media.get('url', '')
                            break
                
                # Si no se encontró en media_content, buscar en otros campos comunes
                if not image_url and hasattr(entry, 'links'):
                    for link_item in entry.links:
                        if link_item.get('type', '').startswith('image/'):
                            image_url = link_item.get('href', '')
                            break
                
                # Buscar en enclosures
                if not image_url and hasattr(entry, 'enclosures'):
                    for enclosure in entry.enclosures:
                        if enclosure.get('type', '').startswith('image/'):
                            image_url = enclosure.get('href', '')
                            break
                
                # Buscar en campos específicos como media_thumbnail
                if not image_url and hasattr(entry, 'media_thumbnail'):
                    image_url = entry.media_thumbnail[0].get('url', '') if entry.media_thumbnail else ''
                
                # Buscar en el contenido usando expresiones regulares
                if not image_url:
                    content = entry.get('content', [{}])[0].get('value', '') if hasattr(entry, 'content') else ''
                    content = content or entry.get('description', '')
                    
                    # Buscar URLs de imágenes en el contenido HTML
                    img_pattern = r'<img[^>]+src="([^">]+)"'
                    images = re.findall(img_pattern, content)
                    if images:
                        image_url = images[0]

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