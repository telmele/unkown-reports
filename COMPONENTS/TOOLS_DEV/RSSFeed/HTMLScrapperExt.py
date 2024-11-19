op.PIP.PrepareModule("requests")
op.PIP.PrepareModule("beautifulsoup4")
import requests
from bs4 import BeautifulSoup
import re

# Importer les modules de support
CustomParHelper: CustomParHelper = next(d for d in me.docked if 'ExtUtils' in d.tags).mod('CustomParHelper').CustomParHelper
NoNode: NoNode = next(d for d in me.docked if 'ExtUtils' in d.tags).mod('NoNode').NoNode

class HTMLScrapperExt:
    def __init__(self, ownerComp):
        # Enregistrer la référence au composant propriétaire
        self.ownerComp = ownerComp
        
        # Initialiser les helpers CustomParHelper et NoNode
        CustomParHelper.Init(self, ownerComp, enable_properties=True, enable_callbacks=True)
        NoNode.Init(ownerComp, enable_chopexec=True, enable_datexec=True, enable_parexec=True, enable_keyboard_shortcuts=True)

    def refresh_feed(self):
        """Appelé lorsque le paramètre Refresh est déclenché."""
        # Obtenir l'URL de la page à scrapper à partir du paramètre URL
        page_url = self.ownerComp.par.Rssurl.eval()
        if not page_url:
            # Afficher un message de débogage si l'URL n'est pas définie
            debug("No page URL defined.")
            return

        # Récupérer les données de la page
        reports_data = self.scrape_page(page_url)
        if reports_data:
            # Mettre à jour la table avec les données des rapports
            self.update_table(reports_data)
        else:
            # Afficher un message de débogage si la récupération ou l'analyse échoue
            debug("Failed to fetch or parse the page.")

    def scrape_page(self, url):
        """Télécharge et analyse la page pour extraire les informations des rapports."""
        try:
            # Faire une requête pour récupérer le contenu de la page

            response = requests.get(url)

            if response.status_code != 200:
                debug(f"Failed to retrieve the page. Status code: {response.status_code}")
                return None
            
            # Analyser le contenu de la page avec BeautifulSoup
            page_content = response.text
            print(page_content)
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Extraire les divs contenant chaque rapport
            reports = []
            report_divs = soup.find_all('div', class_='fe-block')
            for div in report_divs:
                # Extraire la date et la description du rapport
                text_block = div.find('div', class_='sqs-block-content')
                print(text_block)
                if text_block:
                    date = text_block.find('p').text.strip()  # La date se trouve dans un <p>
                    description = text_block.find_all('p')[1].text.strip()  # La description est dans un autre <p>
                else:
                    date = 'No Date'
                    description = 'No Description'

                # Extraire l'image associée
                image_div = div.find('div', class_='image-block-outer-wrapper')
                img_tag = image_div.find('img') if image_div else None
                img_link = img_tag['src'] if img_tag else 'No Image'

                # Ajouter les informations extraites à la liste des rapports
                reports.append([date, description, img_link])
            return reports
        except Exception as e:
            # Afficher un message de débogage si une exception se produit lors de la récupération de la page
            debug(f"Error fetching page data: {e}")
            return None

    def update_table(self, data):
        """Met à jour une Table DAT avec les données des rapports."""
        # Obtenir une référence à la Table DAT 'reports_table'
        table = self.ownerComp.op('reports_table')
        if not table:
            # Afficher un message de débogage si la Table DAT n'est pas trouvée
            debug("reports_table not found in the component.")
            return

        # Effacer les données actuelles de la table
        table.clear()
        # Ajouter une ligne d'en-têtes à la table
        table.appendRow(['Date', 'Description', 'Image Link'])
        # Ajouter chaque entrée du rapport à la table
        for row in data:
            table.appendRow(row)
            
    
    def onParRefresh(self, _par):
    	self.refresh_feed()
