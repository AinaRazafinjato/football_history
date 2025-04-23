import pandas as pd
from pathlib import Path
from constant import TEAM_NAME_CORRECTIONS

# Constantes
ROWS_TO_DROP = ['Date', 'Home', 'Away', 'Venue']  # Colonnes nécessaires pour éviter les lignes incomplètes
COLUMNS_TO_DROP = ['Day', 'Time', 'xG', 'xG.1', 'Match Report', 'Notes']  # Colonnes inutiles à supprimer
REQUIRED_COLUMNS = ['Score', 'Wk', 'Attendance']  # Colonnes obligatoires pour le traitement
COLS_TO_CONVERT = ['Wk', 'Score_Home', 'Score_Away', 'Attendance']  # Colonnes à convertir en valeurs numériques
COLS_ORDER = ['Wk', 'Date', 'Home', 'Score_Home', 'Score_Away', 'Away', 'Venue', 'Attendance', 'Referee']  # Ordre final des colonnes

# Définir le répertoire de base et le répertoire des fichiers CSV
BASE_DIR = Path(__file__).parent
CSV_DIR = BASE_DIR / "csv"
CSV_DIR.mkdir(exist_ok=True, mode=0o755)  # Crée le répertoire CSV s'il n'existe pas


def fetch_table_from_url(url):
    """
    Récupère la première table HTML d'une URL donnée en utilisant pandas.

    Args:
        url (str): L'URL de la page FBref.

    Returns:
        pd.DataFrame: La première table extraite de l'URL.
    """
    try:
        tables = pd.read_html(url)
        return tables[0]
    except Exception as e:
        raise ValueError(f"Erreur lors de la récupération de la table depuis l'URL : {e}")


def clean_and_transform_data(df):
    """
    Nettoie et transforme les données extraites de FBref.

    Args:
        df (pd.DataFrame): Le DataFrame brut contenant les données.

    Returns:
        pd.DataFrame: Le DataFrame nettoyé et transformé.
    """
    # Supprimer les lignes avec des valeurs manquantes dans les colonnes clés
    df = df.dropna(subset=ROWS_TO_DROP)
    
    # Supprimer les colonnes inutiles
    df = df.drop(columns=COLUMNS_TO_DROP, errors='ignore')

    # Vérifier que toutes les colonnes obligatoires sont présentes
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            raise ValueError(f"Colonne obligatoire manquante : {col}")

    # Diviser la colonne 'Score' en deux colonnes : 'Score_Home' et 'Score_Away'
    df[['Score_Home', 'Score_Away']] = df['Score'].str.split('–', expand=True)

    # Convertir les colonnes de score en valeurs numériques, les erreurs deviennent NaN
    df['Score_Home'] = pd.to_numeric(df['Score_Home'], errors='coerce')
    df['Score_Away'] = pd.to_numeric(df['Score_Away'], errors='coerce')

    # Supprimer la colonne originale 'Score'
    df = df.drop('Score', axis=1)

    # Réorganiser les colonnes dans l'ordre souhaité
    df = df[COLS_ORDER]
    
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
    df['Home'] = df['Home'].apply(normalize_team_name)
    df['Away'] = df['Away'].apply(normalize_team_name)

    # Convertir les colonnes spécifiques en entiers si possible, sinon garder None
    for col in COLS_TO_CONVERT:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
        
    return df


def generate_csv_filename(url, df):
    """
    Génère un nom de fichier CSV basé sur l'URL et la saison extraite du DataFrame.

    Args:
        url (str): L'URL de la page FBref.
        df (pd.DataFrame): Le DataFrame contenant les données.

    Returns:
        str: Le nom du fichier CSV généré.
    """
    # Convertir la colonne 'Date' en format datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    if df['Date'].dropna().empty:
        raise ValueError("Aucune date valide trouvée dans le DataFrame.")
    
    # Extraire l'année de début et l'année de fin
    start_year = df['Date'].min().year
    end_year = df['Date'].max().year
    season = f"{start_year}-{end_year}"
    
    # Extraire le nom de la ligue en excluant certains mots
    def extract_league_name(url):
        """
        Extrait le nom de la ligue à partir de l'URL.

        Args:
            url (str): L'URL de la page FBref.

        Returns:
            str: Le nom de la ligue.
        """
        last_part = url.split('/')[-1]
        elements = last_part.split('-')
        exclude = {"Scores", "and", "Fixtures"}
        league_parts = [el for el in elements if el not in exclude]
        return "-".join(league_parts)
    
    league_name = extract_league_name(url)
    
    return f"{league_name}-{season}.csv"


def save_to_csv(df, filename):
    """
    Sauvegarde le DataFrame dans un fichier CSV.

    Args:
        df (pd.DataFrame): Le DataFrame à sauvegarder.
        filename (str): Le nom du fichier CSV.
    """
    csv_path = CSV_DIR / filename
    df.to_csv(csv_path, index=False)


def process_fbref_data(url):
    """
    Traite les données FBref à partir de l'URL donnée et les sauvegarde dans un fichier CSV.

    Args:
        url (str): L'URL de la page FBref contenant les scores et les matchs.

    Returns:
        pd.DataFrame: Le DataFrame traité.
    """
    # Récupérer et nettoyer les données
    raw_data = fetch_table_from_url(url)
    cleaned_data = clean_and_transform_data(raw_data)
    
    # Générer le nom du fichier CSV et sauvegarder les données
    csv_filename = generate_csv_filename(url, cleaned_data)
    save_to_csv(cleaned_data, csv_filename)
    
    return cleaned_data


# Utilisation
if __name__ == "__main__":
    url = "https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures"
    
    try:
        df = process_fbref_data(url)
        print("Les données ont été traitées et sauvegardées avec succès.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")