op.PIP.PrepareModule("feedparser")
import feedparser
import json
# Importer les modules de support
CustomParHelper: CustomParHelper = next(d for d in me.docked if 'ExtUtils' in d.tags).mod('CustomParHelper').CustomParHelper
NoNode: NoNode = next(d for d in me.docked if 'ExtUtils' in d.tags).mod('NoNode').NoNode

class RSSFeedExt:
    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
        # Initialiser les helpers
        CustomParHelper.Init(self, ownerComp, enable_properties=True, enable_callbacks=True)
        NoNode.Init(ownerComp, enable_chopexec=True, enable_datexec=True, enable_parexec=True, enable_keyboard_shortcuts=True)

    def refresh_feed(self):
        """Appelé lorsque le paramètre Refresh est déclenché."""
        rss_url = self.ownerComp.par.Rssurl.eval()
        if not rss_url:
            debug("No RSS URL defined.")
            return

        feed_data = self.fetch_rss(rss_url)
        if feed_data:
            self.update_table(feed_data)
        else:
            debug("Failed to fetch or parse the RSS feed.")

    def fetch_rss(self, url):
        """Télécharge et analyse le flux RSS."""
        try:
            feed = feedparser.parse(url)
            if feed.bozo:  # Vérifier si une erreur est survenue lors de l'analyse
                debug(f"Error parsing RSS feed: {feed.bozo_exception}")
                return None
            
            entries = []
            for entry in feed.entries:
                title = entry.get('title', 'No Title')
                link = entry.get('link', 'No Link')
                summary = entry.get('summary', 'No Summary')
                # Extraire le texte entre les balises <p>
                p_text_match = re.search(r'<p class="">(.*?)</p>', summary, re.DOTALL)
                p_text = p_text_match.group(1) if p_text_match else 'No Text'
                
                # Extraire le lien src de la balise <figure>
                figure_src_match = re.search(r'<figure.*?<img.*?src=["\'](.*?)["\']', summary, re.DOTALL)
                figure_src = figure_src_match.group(1) if figure_src_match else 'No Image'

                entries.append([title, link, p_text, figure_src])
            return entries
        except Exception as e:
            debug(f"Error fetching RSS feed: {e}")
            return None

    def update_table(self, data):
        """Met à jour une Table DAT avec les données RSS."""
        table = self.ownerComp.op('rss_table')
        if not table:
            debug("rss_table not found in the component.")
            return

        table.clear()
        table.appendRow(['Title', 'Link', 'Desc', 'Img'])  # En-têtes
        for row in data:
            table.appendRow(row)

  # _par can be omitted if not needed