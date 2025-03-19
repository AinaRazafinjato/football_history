import pandas as pd

# Chemin du fichier CSV (un niveau au-dessus dans le dossier 'csv')
csv_path = "../../../../csv/Premier-League-2023-2024.csv"
    
# Extraire le nom de la ligue à partir du nom du fichier
league_name = csv_path.split('/')[-1].split("-")[0:2]
league_name = f"{league_name[0]} {league_name[1]}"
matches_df = pd.read_csv(csv_path)
unique_teams = list(matches_df['Home'].drop_duplicates().sort_values())
print(unique_teams)