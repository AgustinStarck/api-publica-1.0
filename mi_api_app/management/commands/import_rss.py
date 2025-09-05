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
        urls = urls = [
            "http://feeds.bbci.co.uk/news/world/rss.xml",                 # BBC World
            "https://rss.cnn.com/rss/edition_world.rss",                  # CNN World
            "https://www.aljazeera.com/xml/rss/all.xml",                  # Al Jazeera
            "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",     # The New York Times - World
            "https://www.theguardian.com/world/rss",                      # The Guardian - World
            "https://www.reutersagency.com/feed/?best-topics=world",      # Reuters World
            "https://feeds.nbcnews.com/nbcnews/public/world",             # NBC News
            "https://feeds.a.dj.com/rss/RSSWorldNews.xml",                # Wall Street Journal - World
            "https://www.ft.com/rss/world",                               # Financial Times
            "https://rss.politico.com/playbook.xml",                # Politico World
            "https://www.france24.com/en/rss",                            # France24 English
            "https://english.kyodonews.net/rss/news",                     # Kyodo News (Japón)
            "https://www.dw.com/atom/rss-en-all",                         # Deutsche Welle (Alemania)
            "https://www.npr.org/rss/rss.php?id=1004",                    # NPR - World

            # 🇦🇷 ARGENTINA
            "https://www.clarin.com/rss/lo-ultimo/",                      # Clarín - Lo Último
            "https://www.clarin.com/rss/mundo/",                          # Clarín - Mundo
            "https://www.lanacion.com.ar/rssfeed/",                       # La Nación - General
            "https://www.pagina12.com.ar/rss/portada",                    # Página/12 - Portada
            "https://www.perfil.com/rss/feed.xml",                        # Perfil - General
            "https://www.lavoz.com.ar/rss/ultimas-noticias.xml",          # La Voz del Interior
            "https://www.ambito.com/rss/ultimas-noticias.xml",            # Ámbito Financiero
            "https://www.cronista.com/files/rss/ultimas-noticias.xml",    # El Cronista
            "https://www.telam.com.ar/rss2/ultimasnoticias.xml",          # Télam
            "https://www.rionegro.com.ar/feed/",                          # Diario Río Negro
            "https://www.lagaceta.com.ar/rss/rss.xml",                    # La Gaceta (Tucumán)
            "https://www.losandes.com.ar/feed/",                          # Los Andes (Mendoza)
            "https://www.diariouno.com.ar/feed",                          # Diario Uno (Mendoza)
            "https://www.eldia.com/rss/ultimas-noticias.xml",             # Diario El Día (La Plata)
            "https://www.baenegocios.com/rss/feed.xml",                   # BAE Negocios
            "https://www.minutouno.com/rss",                              # Minuto Uno

            # 🇧🇷 BRASIL
            "https://g1.globo.com/rss/g1/",                               # G1 (Globo)
            "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml",     # Folha de São Paulo
            "https://rss.uol.com.br/feed/noticias.xml",                   # UOL Notícias

            # 🇲🇽 MÉXICO              
            "https://www.jornada.com.mx/rss/edicion.xml",                 # La Jornada
            "https://www.milenio.com/rss",               # Milenio

            # 🇪🇸 ESPAÑA
            "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",  # El País - Portada
            "https://ep00.epimg.net/rss/elpais/internacional.xml",        # El País - Internacional
            "https://www.abc.es/rss/feeds/abc_ultima.xml",                # ABC España
            "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml",       # El Mundo

            # 📰 GOOGLE NEWS (cambia "hl", "gl", "ceid" según idioma/país)
            "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",      # USA (Inglés)
            "https://news.google.com/rss?hl=en-GB&gl=GB&ceid=GB:en",      # Reino Unido
            "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",      # India (Inglés)
            "https://news.google.com/rss?hl=es-419&gl=AR&ceid=AR:es-419", # Argentina
            "https://news.google.com/rss?hl=es-419&gl=MX&ceid=MX:es-419", # México
            "https://news.google.com/rss?hl=es&gl=ES&ceid=ES:es",         # España
            "https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419",  # Brasil
            "https://news.google.com/rss?hl=fr&gl=FR&ceid=FR:fr",         # Francia
            "https://news.google.com/rss?hl=de&gl=DE&ceid=DE:de",         # Alemania
            "https://news.google.com/rss?hl=it&gl=IT&ceid=IT:it",         # Italia
            "https://news.google.com/rss?hl=ru&gl=RU&ceid=RU:ru",         # Rusia
            "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja",         # Japón
            "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans", # China (Simplificado)
            "https://news.google.com/rss?hl=zh-TW&gl=TW&ceid=TW:zh-Hant", # Taiwán (Tradicional)
            "https://news.google.com/rss?hl=ar&gl=EG&ceid=EG:ar",         # Medio Oriente (Egipto - Árabe)
            "https://news.google.com/rss?hl=en-AU&gl=AU&ceid=AU:en",      # Australia
            "https://news.google.com/rss?hl=en-CA&gl=CA&ceid=CA:en",      # Canadá (Inglés)
            "https://news.google.com/rss?hl=fr-CA&gl=CA&ceid=CA:fr",      # Canadá (Francés)
            "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko",         # Corea del Sur    
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