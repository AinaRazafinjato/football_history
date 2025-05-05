import os
import sys
import django
import pandas as pd
import argparse
from pathlib import Path
from loguru import logger
from typing import Dict, Tuple, List, Optional

# Constants
LOG_FILE = "logs/import_data.log"
LOG_ROTATION = "10 MB"
LOG_RETENTION = "10 days"
LOG_LEVEL = "INFO"
DEFAULT_CSV_FILENAME = "Premier-League-2024-2025.csv"

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
from matches.models import Season, League, Team, MatchDay, Match

# Configurer Loguru
os.makedirs(Path(LOG_FILE).parent, exist_ok=True)  # Créer le dossier de logs s'il n'existe pas
logger.add(LOG_FILE, rotation=LOG_ROTATION, retention=LOG_RETENTION, level=LOG_LEVEL)


def extract_league_name(csv_filename: str) -> str:
    """Extrait le nom de la ligue à partir du nom de fichier CSV"""
    parts = csv_filename.split("-")[0:2]
    return f"{parts[0]} {parts[1]}"


def load_match_data(csv_path: Path) -> pd.DataFrame:
    """Charge et prépare les données de match depuis un CSV"""
    logger.info(f"Chargement du fichier CSV : {csv_path}")
    
    matches_df = pd.read_csv(csv_path)
    logger.info("Données CSV chargées avec succès.")
    
    # Convertir les dates en format datetime
    matches_df['Date'] = pd.to_datetime(matches_df['Date'], errors='coerce')
    return matches_df


def get_season_info(matches_df: pd.DataFrame) -> Tuple[str, str, str]:
    """Extrait les informations de la saison à partir des données de matchs"""
    start_date = matches_df['Date'].min().date()
    end_date = matches_df['Date'].max().date()
    season_name = f"{start_date.year}-{end_date.year}"
    logger.info(f"Saison déterminée : {season_name} ({start_date} à {end_date})")
    return season_name, start_date, end_date


def create_or_update_teams(matches_df: pd.DataFrame) -> Tuple[Dict[str, Team], List[Tuple[str, bool]]]:
    """Crée ou met à jour les équipes dans la base de données"""
    unique_teams = list(matches_df['Home'].drop_duplicates().sort_values())
    teams = {}
    team_results = []
    
    for team_name in unique_teams:
        if pd.isna(team_name):
            logger.warning(f"Équipe ignorée: nom invalide (NaN)")
            continue
            
        team_obj, created = Team.objects.update_or_create(
            team_name=team_name,
            defaults={}
        )
        teams[team_name] = team_obj
        team_results.append((team_name, created))
        
        if created:
            logger.info(f"Nouvelle équipe créée : {team_name}")
        else:
            logger.info(f"Équipe existante mise à jour : {team_name}")
    
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


def create_or_update_league(league_name: str) -> League:
    """Crée ou met à jour la ligue dans la base de données"""
    league, created = League.objects.update_or_create(league_name=league_name)
    if created:
        logger.info(f"Nouvelle ligue créée : {league_name}")
    else:
        logger.info(f"Ligue existante mise à jour : {league_name}")
    return league


def validate_match_row(row: pd.Series) -> bool:
    """Valide une ligne de données de match"""
    required_fields = ['Home', 'Away', 'Date', 'Wk', 'Venue']
    
    for field in required_fields:
        if field not in row or pd.isna(row[field]):
            return False
    
    return True


def import_matches(matches_df: pd.DataFrame, teams: Dict[str, Team], 
                  league: League, season: Season) -> Tuple[int, int]:
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
        if not team_home or not team_away:
            logger.warning(f"Équipe introuvable pour la ligne {index}: {row['Home']} ou {row['Away']}")
            continue

        # Créer ou mettre à jour le MatchDay (journée de match)
        match_day, matchday_created = MatchDay.objects.update_or_create(
            day_number=int(row['Wk']),
            season=season,
            defaults={'day_date': row['Date'].date()}
        )
        
        # Convertir les scores en None si les valeurs sont NaN
        score_home = None if pd.isna(row.get('Score_Home')) else row.get('Score_Home')
        score_away = None if pd.isna(row.get('Score_Away')) else row.get('Score_Away')
        referee = None if 'Referee' not in row or pd.isna(row['Referee']) else row['Referee']

        # Créer ou mettre à jour le match dans la base de données
        match, created = Match.objects.update_or_create(
            match_date=row['Date'].date(),
            team_home=team_home,
            team_away=team_away,
            league=league,
            defaults={
                'score_home': score_home,
                'score_away': score_away,
                'venue': row['Venue'],
                'referee': referee,
                'day': match_day
            }
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
        league_name = extract_league_name(csv_path.name)
        season_name, start_date, end_date = get_season_info(matches_df)
        
        # Créer ou mettre à jour les objets en base de données
        teams, team_results = create_or_update_teams(matches_df)
        season = create_or_update_season(season_name, start_date, end_date)
        league = create_or_update_league(league_name)
        
        # Importer les matchs
        matches_created, matches_updated = import_matches(
            matches_df, teams, league, season)
        
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