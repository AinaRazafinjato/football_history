from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from loguru import logger
import random
import time
from pathlib import Path
import os
import shutil

# Base directory is 3 levels up from the script (to reach football_history root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Configuration du logger
logger.add(
    "logs/scraping_{time}.log",
    rotation="1 day",
    retention="7 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)
logger.add(
    "sys.stdout",
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>"
)

class LogoScraper:
    def __init__(self, url, max_retries=3):
        self.url = url
        self.base_url = "https://www.sofascore.com"
        self.max_retries = max_retries
        self.browser_config = {
            "headless": False,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-site-isolation-trials"
            ]
        }
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "DNT": "1"
        }
        
        # Liste standardisée des équipes attendues
        self.expected_teams = [
            "Arsenal",
            "Aston Villa",
            "Bournemouth",
            "Brentford",
            "Brighton & Hove Albion",
            "Chelsea",
            "Crystal Palace",
            "Everton",
            "Fulham",
            "Ipswich Town",
            "Leicester City",
            "Liverpool",
            "Manchester City",
            "Manchester United",
            "Newcastle United",
            "Nottingham Forest",
            "Southampton",
            "Tottenham Hotspur",
            "West Ham",
            "Wolverhampton Wanderers"
        ]
        
        # Dictionnaire de standardisation des noms
        self.team_name_mapping = {
            # Premier League
            "Man Utd": "Manchester United",
            "Man City": "Manchester City",
            "Tottenham": "Tottenham Hotspur",
            "Wolves": "Wolverhampton Wanderers",
            "Leicester": "Leicester City",
            "Newcastle": "Newcastle United",
            "Brighton": "Brighton & Hove Albion",
            "Forest": "Nottingham Forest",
            "Ipswich": "Ipswich Town",
            # Ajoutez d'autres mappings si nécessaire
        }
        
        self.setup_directories()

    def setup_directories(self):
        """Crée les dossiers pour stocker les logos"""
        
        # Define media directory and logo subdirectories
        self.media_dir = os.path.join(BASE_DIR, "media")
        Path(self.media_dir).mkdir(parents=True, exist_ok=True)
        
        logo_dirs = [
            Path(self.media_dir) / "logos" / "countries",
            Path(self.media_dir) / "logos" / "leagues", 
            Path(self.media_dir) / "logos" / "teams"
        ]
        
        # Create all necessary directories
        for directory in logo_dirs:
            directory.mkdir(parents=True, exist_ok=True)
            
        logger.debug(f"Created logo directories at {self.media_dir}")

    def standardize_name(self, original_name):
        """Standardise le nom de l'équipe selon notre format souhaité"""
        clean_name = original_name.strip()
        
        # Vérifier si le nom est dans notre dictionnaire de mapping
        if clean_name in self.team_name_mapping:
            return self.team_name_mapping[clean_name]
        
        # Vérifier si le nom est déjà dans notre liste d'équipes attendues
        if clean_name in self.expected_teams:
            return clean_name
            
        # Recherche approximative dans notre mapping
        for key, value in self.team_name_mapping.items():
            if key.lower() in clean_name.lower() or clean_name.lower() in key.lower():
                logger.debug(f"Correspondance approx.: '{original_name}' -> '{value}'")
                return value
        
        # Recherche approximative dans notre liste d'équipes attendues
        for expected_team in self.expected_teams:
            if clean_name.lower() in expected_team.lower() or expected_team.lower() in clean_name.lower():
                logger.debug(f"Nom trouvé: '{original_name}' -> '{expected_team}'")
                return expected_team
        
        # Si pas de correspondance, on garde le nom original
        logger.warning(f"Nom d'équipe non reconnu: {original_name}")
        return original_name

    def simulate_human_behavior(self, page):
        """Simule un comportement humain sur la page"""
        actions = [
            lambda: page.mouse.move(random.randint(100, 800), random.randint(100, 600)),
            lambda: page.mouse.wheel(delta_x=0, delta_y=random.randint(-300, 300)),
            lambda: time.sleep(random.uniform(0.5, 2))
        ]
        for _ in range(random.randint(2, 4)):
            random.choice(actions)()

    def download_logo(self, page, url, destination_path):
        """Télécharge un logo depuis l'URL"""
        logger.debug(f"Téléchargement du logo depuis {url}")
        try:
            response = page.goto(url)
            if response.status == 200:
                with open(destination_path, 'wb') as f:
                    f.write(response.body())
                logger.info(f"Logo téléchargé: {destination_path}")
                return True
            logger.warning(f"Échec du téléchargement du logo (status: {response.status}) pour {url}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement: {str(e)}")
            return False

    def process_logo(self, page, url, team_name, country, league, season):
        """Traite et sauvegarde un logo avec nom standardisé directement"""
        try:
            # 1. Standardiser le nom de l'équipe
            standardized_name = self.standardize_name(team_name)
            
            # 2. Créer un nom de fichier sécurisé
            safe_filename = standardized_name.replace("&", "and").replace(" ", "_")
            
            # Sauvegarder directement avec le nom standardisé
            # Define media directory and logo subdirectories
            self.media_dir = os.path.join(BASE_DIR, "media")
            Path(self.media_dir).mkdir(parents=True, exist_ok=True)
            
            team_folder = os.path.join(self.media_dir,'logos/teams', country, league)
            Path(team_folder).mkdir(parents=True, exist_ok=True)
            
            # Utiliser directement le nom standardisé pour le fichier
            logo_path = os.path.join(team_folder, f"{safe_filename}.png")
            
            # Télécharger le logo avec le nom déjà standardisé
            success = self.download_logo(page, url, logo_path)
            
            if success:
                logger.info(f"Logo téléchargé avec nom standardisé: '{team_name}' -> '{standardized_name}'")
            
            return success
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement de {team_name}: {str(e)}")
            return False

    def extract_data(self, soup):
        """Extrait toutes les données de la page"""
        logger.info("Extraction des données de la page")
        tournament_info = soup.find("div", class_="Box Flex WFOdQ ijPrqM")
        if not tournament_info:
            logger.error("Impossible de trouver les informations du tournoi")
            raise ValueError("Tournament info not found")
        
        league_details = tournament_info.find("img", class_="Img bljoYW")
        league_logo = league_details['src']
        league_name = league_details['alt']

        country_details = tournament_info.find("img", class_="Img kKNKoB")
        country_logo = self.base_url + country_details['src']
        country_name = country_details['alt']

        season = tournament_info.find("h2", class_="Text dnkMJl").text.split()[-1].replace("/", "-")

        teams_infos = soup.find_all("a", {"data-testid": "standings_row"})
        teams = []
        for team_info in teams_infos:
            img = team_info.find('img')
            teams.append({
                "logo_url": img['src'],
                "team_name": team_info.find('span').text.strip(),
                "season": season
            })
        logger.info(f"{len(teams)} équipes extraites")

        return {
            "league_logo": league_logo,
            "league_name": league_name,
            "country_logo": country_logo,
            "country_name": country_name,
            "season": season,
            "teams": teams
        }

    def verify_logos(self):
        """Vérifie que tous les logos attendus sont présents"""
        missing = []
        
        # Define media directory and logo subdirectories
        self.media_dir = os.path.join(BASE_DIR, "media")
        Path(self.media_dir).mkdir(parents=True, exist_ok=True)
        
        folder_pattern = os.path.join(self.media_dir, 'logos/teams/*/*')  # Chercher dans tous les sous-dossiers pays/ligues
        
        # Récupérer tous les logos existants
        existing_logos = []
        for folder in Path(os.path.join(self.media_dir, 'logos/teams')).glob('*/*'):
            if not folder.is_dir():
                continue
            for logo_file in folder.glob('*.png'):
                existing_logos.append(logo_file.stem)
        
        # Vérifier les équipes attendues
        for team in self.expected_teams:
            safe_name = team.replace("&", "and").replace(" ", "_")
            if safe_name not in existing_logos:
                missing.append(team)
        
        if missing:
            logger.warning(f"{len(missing)}/{len(self.expected_teams)} logos attendus sont manquants:")
            for team in missing:
                logger.warning(f"- {team}")
        else:
            logger.success(f"Tous les {len(self.expected_teams)} logos attendus sont présents!")
            
        return missing

    def get_page_content(self):
        """Récupère et traite le contenu de la page"""
        for attempt in range(self.max_retries):
            try:
                with sync_playwright() as p:
                    logger.info(f"Tentative {attempt + 1}/{self.max_retries} de récupération de la page")
                    
                    browser = p.chromium.launch(**self.browser_config)
                    logger.debug("Navigateur lancé")
                    context = browser.new_context(
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        extra_http_headers=self.headers
                    )
                    page = context.new_page()
                    page.set_default_timeout(120000)

                    logger.debug(f"Navigation vers {self.url}")
                    response = page.goto(self.url, wait_until="networkidle")
                    
                    if response.status == 403:
                        logger.warning("Accès refusé (403)")
                        continue

                    self.simulate_human_behavior(page)
                    logger.debug("Récupération du contenu HTML de la page")
                    content = page.content()
                    
                    soup = BeautifulSoup(content, 'html.parser')
                    data = self.extract_data(soup)
                    
                    logger.info("Téléchargement des logos...")
                    
                    # Define media directory and logo subdirectories
                    media_dir = os.path.join(BASE_DIR, "media")
                    
                    # Logo du pays
                    country_folder = os.path.join(media_dir, 'logos/countries')
                    country_path = os.path.join(country_folder, f"{data['country_name']}.png")
                    self.download_logo(page, data['country_logo'], country_path)

                    # Logo de la ligue
                    league_folder = os.path.join(media_dir, 'logos/leagues')
                    league_path = os.path.join(league_folder, f"{data['league_name']}.png")
                    self.download_logo(page, data['league_logo'], league_path)

                    # Logos des équipes avec standardisation des noms
                    success_count = 0
                    for team in data['teams']:
                        logger.debug(f"Traitement du logo de l'équipe: {team['team_name']}")
                        if self.process_logo(
                            page, 
                            team['logo_url'],
                            team['team_name'],
                            data['country_name'],
                            data['league_name'],
                            data['season']
                        ):
                            success_count += 1

                    logger.info(f"Logos téléchargés et standardisés: {success_count}/{len(data['teams'])}")
                    
                    # Vérifier les logos standardisés
                    missing_logos = self.verify_logos()
                    
                    browser.close()
                    logger.info("Traitement terminé avec succès")
                    
                    if missing_logos:
                        logger.warning("Certains logos n'ont pas été correctement standardisés")
                    
                    return True

            except PlaywrightTimeout as e:
                logger.warning(f"Timeout: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error("Nombre maximal de tentatives atteint après timeout")
                    raise
                time.sleep(random.uniform(10, 20))
                
            except Exception as e:
                logger.error(f"Erreur: {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error("Nombre maximal de tentatives atteint après erreur")
                    raise
                time.sleep(random.uniform(10, 20))

def main():
    try:
        logger.info("Démarrage du script")
        url = "https://www.sofascore.com/tournament/football/england/premier-league/17"
        scraper = LogoScraper(url)
        scraper.get_page_content()
        logger.info("Script terminé avec succès")
        
    except Exception as e:
        logger.error(f"Erreur critique: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())