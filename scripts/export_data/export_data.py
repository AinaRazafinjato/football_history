import os
import sys
import yaml
import argparse
import pandas as pd
from pathlib import Path
from loguru import logger

def load_config(config_path="config.yaml"):
    """
    Charge la configuration depuis un fichier YAML.
    
    Args:
        config_path (str): Chemin vers le fichier de configuration.
        
    Returns:
        dict: Configuration chargée.
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            logger.info(f"Configuration chargée depuis {config_path}")
            return config
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la configuration: {e}")

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Extraire et transformer les données de football depuis FBref")
    parser.add_argument("--url", help="URL de la page FBref à traiter")
    parser.add_argument("--config", default="config.yaml", help="Chemin vers le fichier de configuration")
    parser.add_argument("--verbose", action="store_true", help="Mode verbeux")
    return parser.parse_args()

# Charger les arguments de ligne de commande
args = parse_arguments()

# Charger la configuration
CONFIG = load_config(args.config)

# Extraire les constantes du fichier de configuration
ROWS_TO_DROP = CONFIG["columns"]["rows_to_drop"]
COLUMNS_TO_DROP = CONFIG["columns"]["columns_to_drop"]
REQUIRED_COLUMNS = CONFIG["columns"]["required_columns"]
COLS_TO_CONVERT_INT = CONFIG["columns"]["cols_to_convert_int"]
COLS_TO_CONVERT_FLOAT = CONFIG["columns"]["cols_to_convert_float"]
COLS_ORDER = CONFIG["columns"]["cols_order"]
TEAM_NAME_CORRECTIONS = CONFIG["team_name_corrections"]

# Définir le répertoire de base et les répertoires des fichiers
BASE_DIR = Path(__file__).parent.parent.parent
CSV_DIR = BASE_DIR / CONFIG["paths"]["csv_dir"]
LOG_DIR = Path(__file__).parent / CONFIG["paths"]["logs_dir"]

# Créer les répertoires s'ils n'existent pas
CSV_DIR.mkdir(exist_ok=True, parents=True, mode=0o755)
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
    level="DEBUG" if args.verbose else "INFO",
    format=FILE_FORMAT,
    colorize=True,
    backtrace=True,
    diagnose=True
)

# Logger pour console - avec couleurs activées
logger.add(
    sys.stdout,
    level="DEBUG" if args.verbose else "INFO",
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
    
    # Supprimer les colonnes inutiles (une seule fois)
    columns_to_drop_existing = [col for col in COLUMNS_TO_DROP if col in df.columns]
    df = df.drop(columns=columns_to_drop_existing, errors='ignore')
    logger.info(f"Colonnes supprimées: {', '.join(columns_to_drop_existing)}")

    # Vérifier que toutes les colonnes obligatoires sont présentes
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            logger.error(f"Colonne obligatoire manquante: {col}")
            raise ValueError(f"Colonne obligatoire manquante : {col}")
        
    # Renommer les colonnes xG et xG.1 en xG_Home et xG_Away avant de les supprimer
    if 'xG' in df.columns:
        df['xG_Home'] = df['xG']
    if 'xG.1' in df.columns:
        df['xG_Away'] = df['xG.1']

    # Convertir les colonnes de xG en valeurs numériques, les erreurs deviennent NaN
    if 'xG_Home' in df.columns:
        df['xG_Home'] = pd.to_numeric(df['xG_Home'], errors='coerce')
    if 'xG_Away' in df.columns:
        df['xG_Away'] = pd.to_numeric(df['xG_Away'], errors='coerce')

    # Diviser la colonne 'Score' en deux colonnes : 'Score_Home' et 'Score_Away'
    if 'Score' in df.columns:
        df[['Score_Home', 'Score_Away']] = df['Score'].str.split('–', expand=True)
        logger.info("Colonne 'Score' divisée en 'Score_Home' et 'Score_Away'")

        # Convertir les colonnes de score en valeurs numériques, les erreurs deviennent NaN
        df['Score_Home'] = pd.to_numeric(df['Score_Home'], errors='coerce')
        df['Score_Away'] = pd.to_numeric(df['Score_Away'], errors='coerce')

        # Supprimer la colonne originale 'Score'
        df = df.drop('Score', axis=1)
    
    # Supprimer les colonnes originales xG et xG.1 si elles existent encore
    columns_to_drop = [col for col in ["xG", "xG.1"] if col in df.columns]
    if columns_to_drop:
        df = df.drop(columns=columns_to_drop, axis=1)

    # Vérifier que toutes les colonnes nécessaires sont présentes pour la réorganisation
    missing_cols = [col for col in COLS_ORDER if col not in df.columns]
    if missing_cols:
        logger.warning(f"Colonnes manquantes pour la réorganisation: {missing_cols}")
        # Ajouter les colonnes manquantes avec des valeurs NULL
        for col in missing_cols:
            df[col] = None

    # Normaliser les noms des équipes dans les colonnes 'Home' et 'Away'
    if 'Home' in df.columns:
        df['Home'] = df['Home'].apply(normalize_team_name)
    if 'Away' in df.columns:
        df['Away'] = df['Away'].apply(normalize_team_name)
    logger.info("Noms d'équipes normalisés")

    # Convertir les colonnes spécifiques en entiers si possible, sinon garder None
    for col in COLS_TO_CONVERT_INT:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
        else:
            logger.warning(f"Colonne {col} non trouvée pour la conversion en entier")

    # Convertir les colonnes spécifiques en float si possible, sinon garder None
    for col in COLS_TO_CONVERT_FLOAT:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('float64')
        else:
            logger.warning(f"Colonne {col} non trouvée pour la conversion en float")
    
    # Réorganiser les colonnes dans l'ordre souhaité (seulement celles qui existent)
    available_cols = [col for col in COLS_ORDER if col in df.columns]
    df = df[available_cols]
    logger.info(f"Colonnes réorganisées dans l'ordre: {', '.join(available_cols)}")
    
    logger.success(f"Données nettoyées avec succès. Dimensions finales: {df.shape}")
    return df

def normalize_team_name(team_name):
    """
    Normalise les noms d'équipes en remplaçant les abréviations et corrections définies.
    
    Args:
        team_name (str): Le nom brut de l'équipe.
    
    Returns:
        str: Le nom normalisé de l'équipe.
    """
    if not isinstance(team_name, str):
        return str(team_name)
        
    words = team_name.split()
    normalized_words = [TEAM_NAME_CORRECTIONS.get(word, word) for word in words]
    return " ".join(filter(None, normalized_words))


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
    if 'Date' not in df.columns:
        logger.error("Colonne 'Date' non trouvée dans le DataFrame")
        raise ValueError("Colonne 'Date' manquante dans le DataFrame")
        
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
    league_name = extract_league_name(url)
    filename = f"{league_name}-{season}.csv"
    logger.info(f"Nom de fichier généré: {filename}")
    
    return filename

def extract_league_name(url):
    """
    Extrait le nom de la ligue à partir de l'URL.

    Args:
        url (str): L'URL de la page FBref.

    Returns:
        str: Le nom de la ligue.
    """
    try:
        last_part = url.split('/')[-1]
        elements = last_part.split('-')
        exclude = {"Scores", "and", "Fixtures"}
        league_parts = [el for el in elements if el not in exclude]
        return "-".join(league_parts)
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du nom de la ligue: {e}")
        return "unknown-league"


def save_to_csv(df, filename):
    """
    Sauvegarde le DataFrame dans un fichier CSV.

    Args:
        df (pd.DataFrame): Le DataFrame à sauvegarder.
        filename (str): Le nom du fichier CSV.
    """
    csv_path = CSV_DIR / filename
    logger.info(f"Sauvegarde des données dans {csv_path}")
    try:
        df.to_csv(csv_path, index=False)
        logger.success(f"Données sauvegardées avec succès dans {csv_path}")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des données: {e}")
        raise IOError(f"Erreur lors de la sauvegarde des données: {e}")


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
    # Utiliser l'URL fournie en argument ou l'URL par défaut de la config
    url = args.url if args.url else CONFIG["urls"]["default"]
    
    try:
        logger.info("Démarrage du script export_data.py")
        df = process_fbref_data(url)
        logger.success("Les données ont été traitées et sauvegardées avec succès.")
    except Exception as e:
        logger.error(f"Une erreur s'est produite: {e}")
        print(f"Une erreur s'est produite : {e}")
        sys.exit(1)