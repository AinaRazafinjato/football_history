import os
import sys
import pandas as pd
from pathlib import Path
from constant import TEAM_NAME_CORRECTIONS
from loguru import logger

# Constantes
ROWS_TO_DROP = ['Date', 'Home', 'Away', 'Venue']  # Colonnes nécessaires pour éviter les lignes incomplètes
COLUMNS_TO_DROP = ['Day', 'Time', 'xG', 'xG.1', 'Match Report', 'Notes']  # Colonnes inutiles à supprimer
REQUIRED_COLUMNS = ['Score', 'Wk', 'Attendance']  # Colonnes obligatoires pour le traitement
COLS_TO_CONVERT = ['Wk', 'Score_Home', 'Score_Away', 'Attendance']  # Colonnes à convertir en valeurs numériques
COLS_ORDER = ['Wk', 'Date', 'Home', 'Score_Home', 'Score_Away', 'Away', 'Venue', 'Attendance', 'Referee']  # Ordre final des colonnes

# Définir le répertoire de base et le répertoire des fichiers CSV
BASE_DIR = Path(__file__).parent.parent.parent
CSV_DIR = os.path.join(BASE_DIR, 'data', 'raw', 'csv')
CSV_DIR = Path(CSV_DIR)  
# Définir le répertoire des logs au même niveau que le script
LOG_DIR = Path(__file__).parent / 'logs'
LOG_DIR = Path(LOG_DIR)

# Créer les répertoires s'ils n'existent pas
CSV_DIR.mkdir(exist_ok=True, mode=0o755)
LOG_DIR.mkdir(exist_ok=True, mode=0o755)

# Configuration améliorée du logger avec des couleurs
logger.remove()  # Supprimer la configuration par défaut

# Format avec couleurs pour le terminal
CONSOLE_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"

# Format avec marqueurs de couleur pour le fichier log
FILE_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"

# Logger pour fichier - avec markup pour préserver les informations de couleur
logger.add(
    os.path.join(LOG_DIR, "export_data_{time:YYYY-MM-DD}.log"),
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format=FILE_FORMAT,
    colorize=True,
    backtrace=True,
    diagnose=True
)

# Logger pour console - avec couleurs activées
logger.add(
    sys.stdout,
    level="INFO",
    format=CONSOLE_FORMAT,
    colorize=True,
    backtrace=True,
    diagnose=True
)

def fetch_table_from_url(url):
    """
    Récupère la première table HTML d'une URL donnée en utilisant pandas.

    Args:
        url (str): L'URL de la page FBref.

    Returns:
        pd.DataFrame: La première table extraite de l'URL.
    """
    try:
        logger.info(f"Tentative de récupération des données depuis: {url}")
        tables = pd.read_html(url)
        logger.success(f"Données récupérées avec succès. {len(tables)} tables trouvées.")
        return tables[0]
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la table depuis l'URL: {e}")
        raise ValueError(f"Erreur lors de la récupération de la table depuis l'URL : {e}")


def clean_and_transform_data(df):
    """
    Nettoie et transforme les données extraites de FBref.

    Args:
        df (pd.DataFrame): Le DataFrame brut contenant les données.

    Returns:
        pd.DataFrame: Le DataFrame nettoyé et transformé.
    """
    logger.info("Début du nettoyage et de la transformation des données")
    
    # Supprimer les lignes avec des valeurs manquantes dans les colonnes clés
    initial_rows = len(df)
    df = df.dropna(subset=ROWS_TO_DROP)
    logger.info(f"{initial_rows - len(df)} lignes supprimées pour données manquantes")
    
    # Supprimer les colonnes inutiles
    df = df.drop(columns=COLUMNS_TO_DROP, errors='ignore')
    logger.info(f"Colonnes supprimées: {', '.join(col for col in COLUMNS_TO_DROP if col in df.columns)}")

    # Vérifier que toutes les colonnes obligatoires sont présentes
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            logger.error(f"Colonne obligatoire manquante: {col}")
            raise ValueError(f"Colonne obligatoire manquante : {col}")

    # Diviser la colonne 'Score' en deux colonnes : 'Score_Home' et 'Score_Away'
    df[['Score_Home', 'Score_Away']] = df['Score'].str.split('–', expand=True)
    logger.info("Colonne 'Score' divisée en 'Score_Home' et 'Score_Away'")

    # Convertir les colonnes de score en valeurs numériques, les erreurs deviennent NaN
    df['Score_Home'] = pd.to_numeric(df['Score_Home'], errors='coerce')
    df['Score_Away'] = pd.to_numeric(df['Score_Away'], errors='coerce')

    # Supprimer la colonne originale 'Score'
    df = df.drop('Score', axis=1)

    # Réorganiser les colonnes dans l'ordre souhaité
    df = df[COLS_ORDER]
    logger.info(f"Colonnes réorganisées dans l'ordre: {', '.join(COLS_ORDER)}")
    
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
    logger.info("Noms d'équipes normalisés")

    # Convertir les colonnes spécifiques en entiers si possible, sinon garder None
    for col in COLS_TO_CONVERT:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
    
    logger.success(f"Données nettoyées avec succès. Dimensions finales: {df.shape}")
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
    logger.info("Génération du nom de fichier CSV")
    
    # Convertir la colonne 'Date' en format datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    if df['Date'].dropna().empty:
        logger.error("Aucune date valide trouvée dans le DataFrame")
        raise ValueError("Aucune date valide trouvée dans le DataFrame.")
    
    # Extraire l'année de début et l'année de fin
    start_year = df['Date'].min().year
    end_year = df['Date'].max().year
    season = f"{start_year}-{end_year}"
    logger.info(f"Saison identifiée: {season}")
    
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
    filename = f"{league_name}-{season}.csv"
    logger.info(f"Nom de fichier généré: {filename}")
    
    return filename


def save_to_csv(df, filename):
    """
    Sauvegarde le DataFrame dans un fichier CSV.

    Args:
        df (pd.DataFrame): Le DataFrame à sauvegarder.
        filename (str): Le nom du fichier CSV.
    """
    csv_path = CSV_DIR / filename
    logger.info(f"Sauvegarde des données dans {csv_path}")
    df.to_csv(csv_path, index=False)
    logger.success(f"Données sauvegardées avec succès dans {csv_path}")


def process_fbref_data(url):
    """
    Traite les données FBref à partir de l'URL donnée et les sauvegarde dans un fichier CSV.

    Args:
        url (str): L'URL de la page FBref contenant les scores et les matchs.

    Returns:
        pd.DataFrame: Le DataFrame traité.
    """
    logger.info(f"Début du traitement des données pour l'URL: {url}")
    
    # Récupérer et nettoyer les données
    raw_data = fetch_table_from_url(url)
    cleaned_data = clean_and_transform_data(raw_data)
    
    # Générer le nom du fichier CSV et sauvegarder les données
    csv_filename = generate_csv_filename(url, cleaned_data)
    save_to_csv(cleaned_data, csv_filename)
    
    logger.success(f"Traitement terminé pour {url}")
    return cleaned_data


# Utilisation
if __name__ == "__main__":
    url = "https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures"
    
    try:
        logger.info("Démarrage du script export_data.py")
        df = process_fbref_data(url)
        logger.success("Les données ont été traitées et sauvegardées avec succès.")
    except Exception as e:
        logger.error(f"Une erreur s'est produite: {e}")
        print(f"Une erreur s'est produite : {e}")