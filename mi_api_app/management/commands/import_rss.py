from django.core.management.base import BaseCommand
from mi_api_app.models import noticias
from mi_api_app.feedrss import get_news_feed
import json
from datetime import datetime

class Command(BaseCommand):
    help = 'Importa noticias desde múltiples feeds RSS a la base de datos'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=5, help='Límite de noticias por feed')
        parser.add_argument('--url', type=str, help='URL específica de un feed (opcional)')

    def handle(self, *args, **options):
        urls = [
            # 🌍 GOOGLE NEWS - GLOBAL
            "https://news.google.com/rss?hl=es-419&gl=US&ceid=US:es-419",
            "https://news.google.com/rss?hl=en&gl=US&ceid=US:en",
            "https://news.google.com/rss/search?q=tecnología&hl=es-419&gl=US&ceid=US:es-419",
            "https://news.google.com/rss/search?q=deportes&hl=es-419&gl=US&ceid=US:es-419",
            "https://news.google.com/rss/search?q=economía&hl=es-419&gl=US&ceid=US:es-419",
            "https://news.google.com/rss/search?q=ciencia&hl=es-419&gl=US&ceid=US:es-419",
            "https://news.google.com/rss/search?q=salud&hl=es-419&gl=US&ceid=US:es-419",
            "https://news.google.com/rss/search?q=política&hl=es-419&gl=US&ceid=US:es-419",

            # 🌍 GOOGLE NEWS - REGIONES
            "https://news.google.com/rss?hl=es-419&gl=AR&ceid=AR:es-419",  # Argentina
            "https://news.google.com/rss?hl=es&gl=ES&ceid=ES:es",          # España
            "https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419",   # Brasil
            "https://news.google.com/rss?hl=fr&gl=FR&ceid=FR:fr",          # Francia
            "https://news.google.com/rss?hl=de&gl=DE&ceid=DE:de",          # Alemania

            # 📰 INTERNACIONALES
            "http://feeds.bbci.co.uk/news/world/rss.xml",                  # BBC Mundo
            "https://elpais.com/rss/elpais/portada.xml",                   # El País (España)
            "https://www.theguardian.com/world/rss",                       # The Guardian
            "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",      # New York Times - Mundo
            "https://feeds.a.dj.com/rss/RSSWorldNews.xml",                 # Wall Street Journal - World
            "https://www.aljazeera.com/xml/rss/all.xml",                   # Al Jazeera
            "https://www.reutersagency.com/feed/?best-topics=world&post_type=best", # Reuters Mundo

            # 🇦🇷 ARGENTINA
            "https://www.clarin.com/rss.html",                             # Clarín
            "https://www.lanacion.com.ar/rss/",                            # La Nación
            "https://www.infobae.com/argentina-rss.xml",                   # Infobae
            "https://www.pagina12.com.ar/rss/portada",                     # Página 12
            "https://www.cronista.com/files/rss/portada.xml",              # El Cronista
            "https://www.ambito.com/rss/ultimas-noticias.xml",             # Ámbito Financiero
            "https://tn.com.ar/rss.xml"                                    # TN Noticias
        ]
        
        limit = options['limit']
        specific_url = options['url']
        
        # Si se especifica una URL, usar solo esa
        if specific_url:
            urls = [specific_url]
        
        total_imported = 0
        total_processed = 0
        
        for i, url in enumerate(urls, 1):
            self.stdout.write(f"\n📡 Procesando feed {i}/{len(urls)}: {url}")
            
            try:
                # Obtener noticias del RSS
                news_json = get_news_feed(url, limit)
                news_list = json.loads(news_json)
                
                count = 0
                for news_item in news_list:
                    # Verificar si la noticia ya existe para evitar duplicados
                    if not noticias.objects.filter(link=news_item['link']).exists():
                        noticias.objects.create(
                            titulo=news_item['title'],
                            descripcion=news_item['description'],
                            site_icon=news_item['site_icon'],
                            link=news_item['link'],
                            image=news_item['image'],
                        )
                        count += 1
                
                total_imported += count
                total_processed += len(news_list)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Importadas {count} nuevas noticias de {len(news_list)} encontradas'
                    )
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  Error procesando {url}: {str(e)}'
                    )
                )
                continue
        
        # Resumen final
        self.stdout.write("\n" + "="*50)
        self.stdout.write(
            self.style.SUCCESS(
                f'🎯 RESUMEN FINAL: Importadas {total_imported} nuevas noticias '
                f'de {total_processed} procesadas desde {len(urls)} feeds'
            )
        )