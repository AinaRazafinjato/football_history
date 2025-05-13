import os
import sys
import django
import pandas as pd
import argparse
from pathlib import Path
from loguru import logger
from typing import Dict, Tuple, List, Optional
import re
# Import constants properly based on how the script is run
try:
    from .constants import TEAM_LOGO_MAPPING, LEAGUE_COUNTRY_MAPPING
except ImportError:
    # When running as a standalone script
    from constants import TEAM_LOGO_MAPPING, LEAGUE_COUNTRY_MAPPING

# Constants
LOG_FILE = "logs/import_data.log"
LOG_ROTATION = "10 MB"
LOG_RETENTION = "10 days"
LOG_LEVEL = "INFO"
DEFAULT_CSV_FILENAME = "Premier-League-2024-2025.csv"
LOGOS_PATH = "static/logos"  # Chemin de base vers les logos
PREMIER_LEAGUE_LOGOS_PATH = "England/Premier League"  # Chemin relatif pour Premier League

# Ajouter le répertoire parent au sys.path pour trouver les modules Django
# Le chemin est relatif à l'emplacement du script
# scripts/import_data -> remonter au répertoire racine du projet Django
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Il est essentiel que le répertoire racine du projet Django soit dans le sys.path
sys.path.insert(0, str(BASE_DIR))

# Configurer l'environnement Django
# Utilisez le module settings exact tel qu'il est nommé dans votre projet
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_history.settings')
django.setup()

# Importer les modèles Django nécessaires
from matches.models import Season, League, LeagueSeason, Team, TeamSeason, MatchDay, Match

# Configurer Loguru
os.makedirs(Path(LOG_FILE).parent, exist_ok=True)  # Créer le dossier de logs s'il n'existe pas
logger.add(LOG_FILE, rotation=LOG_ROTATION, retention=LOG_RETENTION, level=LOG_LEVEL)


def extract_league_and_country(csv_filename: str) -> Tuple[str, str]:
    """Extrait le nom de la ligue et le pays à partir du nom de fichier CSV"""
    parts = csv_filename.split("-")
    league_name = parts[0].strip()
    country = None
    
    # Déterminer le pays en fonction du nom de la ligue
    for league_key, country_value in LEAGUE_COUNTRY_MAPPING.items():
        if league_key in csv_filename:
            country = country_value
            break
    
    # Si le pays est spécifié dans le nom du fichier, l'utiliser
    if len(parts) > 2 and parts[1].strip() in ['England', 'Spain', 'Italy', 'Germany', 'France']:
        country = parts[1].strip()
        league_name = f"{parts[0]}"
    else:
        league_name = f"{parts[0]}"
    
    if league_name == "Premier":
        league_name = "Premier League"
    
    return league_name, country


def get_premier_league_logo_path(team_name: str) -> Optional[str]:
    """
    Fonction spéciale pour obtenir le chemin du logo de Premier League
    """
    if team_name in TEAM_LOGO_MAPPING:
        logo_filename = TEAM_LOGO_MAPPING[team_name]
        logo_path = f"{PREMIER_LEAGUE_LOGOS_PATH}/{logo_filename}"
        full_path = BASE_DIR / LOGOS_PATH / logo_path
        
        # Vérifier si le fichier existe
        if full_path.exists():
            logger.info(f"Logo Premier League trouvé pour {team_name}: {logo_path}")
            return logo_path
    
    return None


def find_logo_path(entity_name: str, entity_type: str, country: str = None, league_name: str = None) -> Optional[str]:
    """
    Trouve le chemin du logo pour une entité (équipe ou ligue)
    
    Args:
        entity_name: Nom de l'entité (équipe ou ligue)
        entity_type: Type d'entité ('teams', 'leagues' ou 'countries')
        country: Pays (pour les équipes)
        league_name: Nom de la ligue (pour les équipes)
    
    Returns:
        Le chemin relatif du logo s'il existe, sinon None
    """
    # Cas spécial pour Premier League
    if country == "England" and league_name == "Premier League" and entity_type == 'teams':
        premier_league_path = get_premier_league_logo_path(entity_name)
        if premier_league_path:
            return premier_league_path
    
    # Vérifier si nous avons une correspondance directe dans le mapping pour les équipes
    if entity_type == 'teams' and entity_name in TEAM_LOGO_MAPPING:
        if country and league_name:
            logo_path = f"{entity_type}/{country}/{league_name}/{TEAM_LOGO_MAPPING[entity_name]}"
            full_path = BASE_DIR / LOGOS_PATH / Path(logo_path)
            if full_path.exists():
                logger.info(f"Logo trouvé pour {entity_name} via mapping: {logo_path}")
                return logo_path
        
        # Si le chemin avec pays et ligue n'existe pas, essayer juste avec le nom du fichier
        logo_path = f"{entity_type}/{TEAM_LOGO_MAPPING[entity_name]}"
        full_path = BASE_DIR / LOGOS_PATH / Path(logo_path)
        if full_path.exists():
            logger.info(f"Logo trouvé pour {entity_name} via mapping (chemin simple): {logo_path}")
            return logo_path
    
    # Pour les équipes avec structure hiérarchique
    if entity_type == 'teams' and country and league_name:
        logos_dir = BASE_DIR / LOGOS_PATH / entity_type / country / league_name
        if logos_dir.exists():
            # Chercher des fichiers qui pourraient correspondre
            for logo_file in logos_dir.glob('*.png'):
                if entity_name.lower() in logo_file.stem.lower() or logo_file.stem.lower() in entity_name.lower():
                    rel_path = f"{entity_type}/{country}/{league_name}/{logo_file.name}"
                    logger.info(f"Logo trouvé pour {entity_name} via recherche hiérarchique: {rel_path}")
                    return rel_path
    
    # Recherche générique dans le dossier de base du type d'entité
    logos_dir = BASE_DIR / LOGOS_PATH / entity_type
    if logos_dir.exists():
        # Normaliser le nom pour la recherche
        normalized_name = re.sub(r'[^a-zA-Z0-9]', '', entity_name.lower())
        
        # Recherche récursive
        for logo_file in logos_dir.glob('**/*.png'):
            normalized_file = re.sub(r'[^a-zA-Z0-9]', '', logo_file.stem.lower())
            # Correspondance exacte ou partielle significative
            if normalized_name == normalized_file or (len(normalized_name) > 3 and normalized_name in normalized_file):
                rel_path = logo_file.relative_to(BASE_DIR / LOGOS_PATH)
                logger.info(f"Logo trouvé pour {entity_name} via recherche générique: {rel_path}")
                return str(rel_path)
    
    logger.warning(f"Aucun logo trouvé pour {entity_name} ({entity_type})")
    return None


def list_all_logos():
    """Affiche tous les logos disponibles pour le débogage"""
    logos_base = BASE_DIR / LOGOS_PATH
    if not logos_base.exists():
        logger.error(f"Dossier de logos non trouvé: {logos_base}")
        return
    
    logger.info(f"Liste des logos disponibles:")
    for logo_file in logos_base.glob('**/*.png'):
        rel_path = logo_file.relative_to(logos_base)
        logger.info(f"  - {rel_path}")


def load_match_data(csv_path: Path) -> pd.DataFrame:
    """Charge et prépare les données de match depuis un CSV"""
    logger.info(f"Chargement du fichier CSV : {csv_path}")
    
    matches_df = pd.read_csv(csv_path)
    logger.info("Données CSV chargées avec succès.")
    
    # Convertir les dates en format datetime
    matches_df['Date'] = pd.to_datetime(matches_df['Date'], errors='coerce')
    
    # Convertir les scores en valeurs numériques (gestion des NaN)
    for col in ['Score_Home', 'Score_Away', 'xG_Home', 'xG_Away']:
        if col in matches_df.columns:
            matches_df[col] = pd.to_numeric(matches_df[col], errors='coerce')
    
    return matches_df


def get_season_info(matches_df: pd.DataFrame) -> Tuple[str, str, str]:
    """Extrait les informations de la saison à partir des données de matchs"""
    start_date = matches_df['Date'].min().date()
    end_date = matches_df['Date'].max().date()
    season_name = f"{start_date.year}-{end_date.year}"
    logger.info(f"Saison déterminée : {season_name} ({start_date} à {end_date})")
    return season_name, start_date, end_date


def create_or_update_teams(matches_df: pd.DataFrame, league: League) -> Tuple[Dict[str, Team], List[Tuple[str, bool]]]:
    """Crée ou met à jour les équipes dans la base de données"""
    # Extraire les noms uniques des équipes (domicile et extérieur)
    home_teams = matches_df['Home'].dropna().unique()
    away_teams = matches_df['Away'].dropna().unique()
    unique_teams = sorted(set(home_teams) | set(away_teams))
    
    teams = {}
    team_results = []
    
    for team_name in unique_teams:
        if pd.isna(team_name):
            logger.warning(f"Équipe ignorée: nom invalide (NaN)")
            continue
        
        # Cas spécial pour Premier League
        logo_path = None
        if league.league_name == "Premier League" and league.country == "England":
            logo_path = get_premier_league_logo_path(team_name)
        
        # Si pas de logo trouvé en Premier League, utiliser la recherche standard
        if not logo_path:
            logo_path = find_logo_path(
                team_name, 
                'teams', 
                country=league.country, 
                league_name=league.league_name
            )
        
        # Créer ou mettre à jour l'équipe
        team_obj, created = Team.objects.update_or_create(
            team_name=team_name,
            defaults={
                'league': league,
                'logo': logo_path
            }
        )
        
        teams[team_name] = team_obj
        team_results.append((team_name, created))
        
        if created:
            logger.info(f"Nouvelle équipe créée : {team_name}" + (f" avec logo: {logo_path}" if logo_path else ""))
        else:
            logger.info(f"Équipe existante mise à jour : {team_name}" + (f" avec logo: {logo_path}" if logo_path else ""))
    
    return teams, team_results


def create_or_update_season(season_name: str, start_date: str, end_date: str) -> Season:
    """Crée ou met à jour la saison dans la base de données"""
    season, created = Season.objects.update_or_create(
        season_name=season_name,
        defaults={'start_date': start_date, 'end_date': end_date}
    )
    if created:
        logger.info(f"Nouvelle saison créée : {season_name}")
    else:
        logger.info(f"Saison existante mise à jour : {season_name}")
    return season


def create_or_update_league(league_name: str, country: Optional[str] = None) -> League:
    """Crée ou met à jour la ligue dans la base de données"""
    # Rechercher un logo pour cette ligue
    logo_path = None
    if league_name == "Premier League" and country == "England":
        # Chemin spécifique pour la Premier League
        specific_logo_path = f"leagues/{country}/{league_name}.png"
        if (BASE_DIR / LOGOS_PATH / specific_logo_path).exists():
            logo_path = specific_logo_path
    
    # Si pas de logo trouvé, utiliser la recherche standard
    if not logo_path:
        logo_path = find_logo_path(league_name, 'leagues', country=country)
    
    # Créer ou mettre à jour la ligue
    league, created = League.objects.update_or_create(
        league_name=league_name,
        defaults={
            'country': country,
            'logo': logo_path
        }
    )
    
    if created:
        logger.info(f"Nouvelle ligue créée : {league_name}" + (f" ({country})" if country else ""))
    else:
        logger.info(f"Ligue existante mise à jour : {league_name}")
    return league


def create_or_update_league_season(league: League, season: Season) -> LeagueSeason:
    """Crée ou met à jour la relation LeagueSeason"""
    league_season, created = LeagueSeason.objects.update_or_create(
        league=league,
        season=season,
        defaults={}
    )
    
    if created:
        logger.info(f"Nouvelle relation League-Season créée : {league_season}")
    else:
        logger.info(f"Relation League-Season existante mise à jour : {league_season}")
    
    return league_season


def create_or_update_team_seasons(teams: Dict[str, Team], league_season: LeagueSeason) -> None:
    """Crée ou met à jour les relations TeamSeason"""
    for team in teams.values():
        team_season, created = TeamSeason.objects.update_or_create(
            team=team,
            league_season=league_season,
            defaults={}
        )
        
        if created:
            logger.debug(f"Nouvelle relation Team-Season créée : {team_season}")


def validate_match_row(row: pd.Series) -> bool:
    """Valide une ligne de données de match"""
    required_fields = ['Home', 'Away', 'Date', 'Wk']
    
    for field in required_fields:
        if field not in row or pd.isna(row[field]):
            return False
    
    return True


def import_matches(matches_df: pd.DataFrame, teams: Dict[str, Team], 
                  league_season: LeagueSeason) -> Tuple[int, int]:
    """Importe les données de matchs dans la base de données"""
    matches_created = 0
    matches_updated = 0
    
    for index, row in matches_df.iterrows():
        # Valider les données de la ligne
        if not validate_match_row(row):
            logger.warning(f"Ligne {index} ignorée: données incomplètes")
            continue
            
        # Récupérer les objets des équipes à domicile et à l'extérieur
        team_home = teams.get(row['Home'])
        team_away = teams.get(row['Away'])

        # Vérifier si les équipes existent
        # Créer ou mettre à jour le MatchDay (journée de match)
        match_day, _ = MatchDay.objects.update_or_create(
            day_number=int(row['Wk']),
            league_season=league_season,
            defaults={'day_date': row['Date'].date()}
        )
        
        # Préparer les données du match
        match_data = {
            'day': match_day,
            'match_date': row['Date'].date(),
            'team_home': team_home,
            'team_away': team_away
        }
        
        # Ajouter les champs optionnels s'ils existent
        if 'Time' in row and not pd.isna(row['Time']):
            match_data['time'] = row['Time']
            
        if 'Score_Home' in row and not pd.isna(row['Score_Home']):
            match_data['score_home'] = row['Score_Home']
            
        if 'Score_Away' in row and not pd.isna(row['Score_Away']):
            match_data['score_away'] = row['Score_Away']
            
        if 'xG_Home' in row and not pd.isna(row['xG_Home']):
            match_data['xG_home'] = row['xG_Home']
            
        if 'xG_Away' in row and not pd.isna(row['xG_Away']):
            match_data['xG_away'] = row['xG_Away']
            
        if 'Venue' in row and not pd.isna(row['Venue']):
            match_data['venue'] = row['Venue']
        # Créer ou mettre à jour le match dans la base de données
        _, created = Match.objects.update_or_create(
            match_date=row['Date'].date(),
            team_home=team_home,
            team_away=team_away,
            defaults=match_data
        )
        
        if created:
            logger.info(f"Nouveau match créé : {row['Home']} vs {row['Away']} ({row['Date'].date()})")
            matches_created += 1
        else:
            logger.debug(f"Match existant mis à jour : {row['Home']} vs {row['Away']} ({row['Date'].date()})")
            matches_updated += 1
    
    return matches_created, matches_updated


def main(csv_filename: Optional[str] = None) -> int:
    """Fonction principale d'importation des données"""
    try:
        # Lister tous les logos disponibles pour le débogage
        list_all_logos()
        
        # Permettre de spécifier un nom de fichier en paramètre
        if not csv_filename:
            csv_filename = DEFAULT_CSV_FILENAME
        
        # Vérifier si le dossier data/raw/csv existe
        csv_dir = BASE_DIR / 'data' / 'raw' / 'csv'
        if not csv_dir.exists():
            logger.warning(f"Le répertoire {csv_dir} n'existe pas. Création du répertoire.")
            csv_dir.mkdir(parents=True, exist_ok=True)
        
        csv_path = csv_dir / csv_filename
        
        # Vérifier si le fichier existe
        if not csv_path.exists():
            logger.error(f"Le fichier {csv_path} n'existe pas.")
            return 1
        
        # Charger et préparer les données
        matches_df = load_match_data(csv_path)
        
        # Extraire les informations de la ligue et de la saison
        league_name, country = extract_league_and_country(csv_path.name)
        season_name, start_date, end_date = get_season_info(matches_df)
        
        # Créer ou mettre à jour les objets en base de données
        league = create_or_update_league(league_name, country)
        season = create_or_update_season(season_name, start_date, end_date)
        league_season = create_or_update_league_season(league, season)
        
        # Créer ou mettre à jour les équipes
        teams, team_results = create_or_update_teams(matches_df, league)
        
        # Créer ou mettre à jour les relations TeamSeason
        create_or_update_team_seasons(teams, league_season)
        
        # Importer les matchs
        matches_created, matches_updated = import_matches(
            matches_df, teams, league_season)
        
        # Afficher les statistiques d'importation
        stats = {
            "teams_created": sum(1 for _, created in team_results if created),
            "teams_updated": sum(1 for _, created in team_results if not created),
            "matches_created": matches_created,
            "matches_updated": matches_updated,
            "total_processed": len(matches_df)
        }
        logger.success(f"Données importées avec succès ! Statistiques: {stats}")
        return 0
        
    except FileNotFoundError as e:
        # Gérer le cas où le fichier CSV est introuvable
        logger.error(f"Erreur : Le fichier n'a pas été trouvé. {e}")
        return 1
        
    except Exception as e:
        # Gérer toutes les autres exceptions
        logger.exception(f"Une erreur s'est produite : {e}")
        return 1


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Importe des données de match depuis un CSV")
    parser.add_argument("--csv", help="Nom du fichier CSV à importer")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    exit(main(args.csv))