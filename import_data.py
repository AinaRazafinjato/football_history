import os
import django
import pandas as pd

# Configurer l’environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_history.settings')
django.setup()

# Importer vos modèles
from matches.models import Season, League, Team, MatchDay, Match

try:
    # Chemin du fichier CSV (un niveau au-dessus dans le dossier 'csv')
    csv_path = "../csv/Premier-League-2023-2024.csv"
    
    # Extraire le nom de la ligue à partir du nom du fichier
    league_name = csv_path.split('/')[-1].split("-")[0:2]
    league_name = f"{league_name[0]} {league_name[1]}"

    # Charger les données depuis le CSV
    matches_df = pd.read_csv(csv_path)

    # Extraire la saison à partir des dates du CSV
    matches_df['Date'] = pd.to_datetime(matches_df['Date'], errors='coerce')
    start_date = matches_df['Date'].min().date()
    end_date = matches_df['Date'].max().date()
    season_name = f"{start_date.year}-{end_date.year}"

    # Créer ou récupérer la saison
    season, _ = Season.objects.get_or_create(
        season_name=season_name,
        defaults={'start_date': start_date, 'end_date': end_date}
    )

    # Créer ou récupérer la ligue
    league, _ = League.objects.get_or_create(league_name=league_name)

    # Utiliser des ensembles pour éviter les doublons d'équipes
    unique_teams = list(matches_df['Home'].drop_duplicates().sort_values())
    teams = {team: Team.objects.get_or_create(team_name=team)[0] for team in unique_teams}

    # Importer les données
    for index, row in matches_df.iterrows():
        team_home = teams[row['Home']]
        team_away = teams[row['Away']]

        match_day, _ = MatchDay.objects.get_or_create(
            day_number=int(row['Wk']),
            day_date=row['Date'].date(),
            season=season
        )

        Match.objects.create(
            match_date=row['Date'].date(),
            score_home=row['Score_Home'],
            score_away=row['Score_Away'],
            venue=row['Venue'],
            day=match_day,
            league=league,
            team_home=team_home,
            team_away=team_away
        )
        

    print("Données importées avec succès !")

except FileNotFoundError:
    print("Erreur : Le fichier CSV n'a pas été trouvé. Vérifiez le chemin.")
except Exception as e:
    print(f"Une erreur s'est produite : {e}")