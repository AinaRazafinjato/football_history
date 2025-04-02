import os
import django
import pandas as pd
import logging

TEAM_NAME_CORRECTIONS = {
    
    # Premier League
    "Utd": "United",
    "Nott'ham": "Nottingham",
    "Wolves": "Wolverhampton",
}


# Configurer l’environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_history.settings')
django.setup()

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importer vos modèles
from matches.models import Season, League, Team, MatchDay, Match

try:
    # Chemin du fichier CSV
    # Importer un par un les fichiers csv
    csv_path = "csv/Premier-League-2024-2025.csv"
    
    # Extraire le nom de la ligue à partir du nom du fichier
    league_parts = csv_path.split('/')[-1].split("-")[0:2]
    league_name = f"{league_parts[0]} {league_parts[1]}"
    logger.info(f"Nom de la ligue extrait : {league_name}")

    # Charger les données depuis le CSV
    matches_df = pd.read_csv(csv_path)
    logger.info("CSV chargé avec succès.")
    
    # Fonction pour normaliser les noms d'équipes
    def normalize_team_name(team_name):
        """
        Normalise les noms d'équipes en remplaçant les abréviations et corrections définies.
        
        Args:
            team_name (str): Le nom brut de l'équipe.
        
        Returns:
            str: Le nom normalisé de l'équipe.
        """
        words = team_name.split()
        normalized_words = [TEAM_NAME_CORRECTIONS.get(word, word) for word in words]
        return " ".join(filter(None, normalized_words))

    
    # Normalisations des nombre des équipes
    matches_df['Home'] = matches_df['Home'].apply(normalize_team_name)
    matches_df['Away'] = matches_df['Away'].apply(normalize_team_name)
    

    # Extraire la saison à partir des dates du CSV
    matches_df['Date'] = pd.to_datetime(matches_df['Date'], errors='coerce')
    start_date = matches_df['Date'].min().date()
    end_date = matches_df['Date'].max().date()
    season_name = f"{start_date.year}-{end_date.year}"
    logger.info(f"Saison extraite : {season_name} (du {start_date} au {end_date})")

    # Créer ou récupérer la saison
    season, created_season = Season.objects.get_or_create(
        season_name=season_name,
        defaults={'start_date': start_date, 'end_date': end_date}
    )
    if created_season:
        logger.info("Nouvelle saison créée.")
    else:
        logger.info("Saison existante récupérée.")

    # Créer ou récupérer la ligue
    league, created_league = League.objects.get_or_create(league_name=league_name)
    if created_league:
        logger.info("Nouvelle ligue créée.")
    else:
        logger.info("Ligue existante récupérée.")

    # Utiliser des ensembles pour éviter les doublons d'équipes
    unique_teams = list(matches_df['Home'].drop_duplicates().sort_values())
    teams = {}
    for team_name in unique_teams:
        team_obj, created_team = Team.objects.get_or_create(team_name=team_name)
        teams[team_name] = team_obj
        if created_team:
            logger.info(f"Équipe créée : {team_name}")
        else:
            logger.info(f"Équipe existante récupérée : {team_name}")

    # Importer les données des matchs
    for index, row in matches_df.iterrows():
        team_home = teams.get(row['Home'])
        team_away = teams.get(row['Away'])
        if not team_home or not team_away:
            logger.warning(f"Équipe introuvable pour la ligne {index}: {row['Home']} ou {row['Away']}")
            continue

        match_day, created_day = MatchDay.objects.get_or_create(
            day_number=int(row['Wk']),
            day_date=row['Date'].date(),
            season=season
        )
        if created_day:
            logger.info(f"MatchDay créé pour la semaine {row['Wk']} le {row['Date'].date()}.")
        else:
            logger.info(f"MatchDay existant pour la semaine {row['Wk']} le {row['Date'].date()}.")

        # Convertir les NaN en None pour l'importation
        score_home = None if pd.isna(row['Score_Home']) else row['Score_Home']
        score_away = None if pd.isna(row['Score_Away']) else row['Score_Away']
        
        Match.objects.create(
            match_date=row['Date'].date(),
            score_home=score_home,
            score_away=score_away, 
            venue=row['Venue'],
            referee=row['Referee'],
            day=match_day,
            league=league,
            team_home=team_home,
            team_away=team_away
        )
        logger.info(f"Match créé : {row['Home']} vs {row['Away']} le {row['Date'].date()}.")

    logger.info("Données importées avec succès !")

except FileNotFoundError:
    logger.error("Erreur : Le fichier CSV n'a pas été trouvé. Vérifiez le chemin.")
except Exception as e:
    logger.exception(f"Une erreur s'est produite : {e}")
