import os
import django
import pandas as pd
import logging

# Dictionnaire pour corriger les noms d'équipes
TEAM_NAME_CORRECTIONS = {
    # Premier League
    "Utd": "United",
    "Nott'ham": "Nottingham",
    "Wolves": "Wolverhampton",
}

# Configurer le logging pour enregistrer les informations et les erreurs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("import_data.log"),  # Enregistrer les logs dans un fichier
        logging.StreamHandler()  # Afficher les logs dans la console
    ]
)
logger = logging.getLogger(__name__)

# Configurer l’environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_history.settings')
django.setup()

# Importer les modèles Django nécessaires
from matches.models import Season, League, Team, MatchDay, Match

try:
    # Chemin du fichier CSV contenant les données des matchs
    csv_path = "csv/Premier-League-2024-2025.csv"
    logger.info(f"Chargement du fichier CSV : {csv_path}")
    
    # Extraire le nom de la ligue à partir du nom du fichier
    league_name = csv_path.split('/')[-1].split("-")[0:2]
    league_name = f"{league_name[0]} {league_name[1]}"
    logger.info(f"Nom de la ligue extrait : {league_name}")

    # Charger les données depuis le fichier CSV
    matches_df = pd.read_csv(csv_path)
    logger.info("Données CSV chargées avec succès.")

    # Convertir les dates en format datetime et extraire les dates de début et de fin de la saison
    matches_df['Date'] = pd.to_datetime(matches_df['Date'], errors='coerce')
    start_date = matches_df['Date'].min().date()
    end_date = matches_df['Date'].max().date()
    season_name = f"{start_date.year}-{end_date.year}"
    logger.info(f"Saison déterminée : {season_name} ({start_date} à {end_date})")
    
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

    # Normaliser les noms des équipes dans les colonnes 'Home' et 'Away'
    matches_df['Home'] = matches_df['Home'].apply(normalize_team_name)
    matches_df['Away'] = matches_df['Away'].apply(normalize_team_name)
    
    # Créer ou mettre à jour les équipes dans la base de données
    unique_teams = list(matches_df['Home'].drop_duplicates().sort_values())
    teams = {}
    for team_name in unique_teams:
        team_obj, created = Team.objects.update_or_create(
            team_name=team_name,
            defaults={}
        )
        teams[team_name] = team_obj
        if created:
            logger.info(f"Nouvelle équipe créée : {team_name}")
        else:
            logger.info(f"Équipe existante mise à jour : {team_name}")

    # Créer ou mettre à jour la saison dans la base de données
    season, created = Season.objects.update_or_create(
        season_name=season_name,
        defaults={'start_date': start_date, 'end_date': end_date}
    )
    if created:
        logger.info(f"Nouvelle saison créée : {season_name}")
    else:
        logger.info(f"Saison existante mise à jour : {season_name}")

    # Créer ou mettre à jour la ligue dans la base de données
    league, created = League.objects.update_or_create(league_name=league_name)
    if created:
        logger.info(f"Nouvelle ligue créée : {league_name}")
    else:
        logger.info(f"Ligue existante mise à jour : {league_name}")

    # Parcourir les données des matchs et les importer dans la base de données
    for index, row in matches_df.iterrows():
        # Récupérer les objets des équipes à domicile et à l'extérieur
        team_home = teams.get(row['Home'])
        team_away = teams.get(row['Away'])

        # Vérifier si les équipes existent
        if not team_home or not team_away:
            logger.warning(f"Équipe introuvable pour la ligne {index}: {row['Home']} ou {row['Away']}")
            continue

        # Créer ou mettre à jour le MatchDay (journée de match)
        match_day, created = MatchDay.objects.update_or_create(
            day_number=int(row['Wk']),
            season=season,
            defaults={'day_date': row['Date'].date()}
        )
        if created:
            logger.info(f"Nouveau MatchDay créé : Semaine {row['Wk']} ({row['Date'].date()})")
        else:
            logger.info(f"MatchDay existant mis à jour : Semaine {row['Wk']} ({row['Date'].date()})")

        # Convertir les scores en None si les valeurs sont NaN
        score_home = None if pd.isna(row['Score_Home']) else row['Score_Home']
        score_away = None if pd.isna(row['Score_Away']) else row['Score_Away']

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
                'referee': row['Referee'] if 'Referee' in row else None,
                'day': match_day
            }
        )
        if created:
            logger.info(f"Nouveau match créé : {row['Home']} vs {row['Away']} ({row['Date'].date()})")
        else:
            logger.info(f"Match existant mis à jour : {row['Home']} vs {row['Away']} ({row['Date'].date()})")

    logger.info("Données importées avec succès !")

except FileNotFoundError:
    # Gérer le cas où le fichier CSV est introuvable
    logger.error("Erreur : Le fichier CSV n'a pas été trouvé. Vérifiez le chemin.")
except Exception as e:
    # Gérer toutes les autres exceptions
    logger.exception(f"Une erreur s'est produite : {e}")