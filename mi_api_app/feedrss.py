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

                news_item = {
                    "title": title[:199],  # Asegurar que no exceda el límite del modelo
                    "description": description[:1000],  # Limitar descripción
                    "site_icon": site_icon,
                    "link": link
                }
                news_list.append(news_item)
                
            except Exception as e:
                logger.error(f"Error procesando entrada en {url}: {e}")
                continue

        return json.dumps(news_list, indent=4, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Error procesando feed {url}: {e}")
        return json.dumps([], ensure_ascii=False)