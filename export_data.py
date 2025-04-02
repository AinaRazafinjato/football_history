import pandas as pd
from pathlib import Path

# Constants
ROWS_TO_DROP = ['Date', 'Home', 'Away', 'Venue']
COLUMNS_TO_DROP = ['Day', 'Time', 'xG', 'xG.1', 'Match Report', 'Notes']
REQUIRED_COLUMNS = ['Score', 'Wk', 'Attendance']
COLS_TO_CONVERT = ['Wk', 'Score_Home', 'Score_Away', 'Attendance']
COLS_ORDER = ['Wk', 'Date', 'Home', 'Score_Home', 'Score_Away', 'Away', 'Venue', 'Attendance', 'Referee']

# Define base directory and CSV directory
BASE_DIR = Path(__file__).parent
CSV_DIR = BASE_DIR / "csv"
CSV_DIR.mkdir(exist_ok=True, mode=0o755)


def fetch_table_from_url(url):
    """
    Fetches the first table from the given URL using pandas.

    Args:
        url (str): The URL of the FBref page.

    Returns:
        pd.DataFrame: The first table from the URL.
    """
    try:
        tables = pd.read_html(url)
        return tables[0]
    except Exception as e:
        raise ValueError(f"Error fetching table from URL: {e}")


def clean_and_transform_data(df):
    """
    Cleans and transforms the FBref data.

    Args:
        df (pd.DataFrame): The raw DataFrame.

    Returns:
        pd.DataFrame: The cleaned and transformed DataFrame.
    """
    # Drop rows with missing key values
    df = df.dropna(subset=ROWS_TO_DROP)
    
    # Drop unnecessary columns
    df = df.drop(columns=COLUMNS_TO_DROP, errors='ignore')

    # Ensure required columns exist
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Split 'Score' column into 'Score_Home' and 'Score_Away'
    df[['Score_Home', 'Score_Away']] = df['Score'].str.split('–', expand=True)

    # Convert score columns to numeric, les erreurs deviennent NaN
    df['Score_Home'] = pd.to_numeric(df['Score_Home'], errors='coerce')
    df['Score_Away'] = pd.to_numeric(df['Score_Away'], errors='coerce')

    # Drop the original 'Score' column
    df = df.drop('Score', axis=1)

    # Reorder columns
    df = df[COLS_ORDER]

    # Convert 'Wk' and 'Attendance' to numeric
    df['Wk'] = pd.to_numeric(df['Wk'], errors='coerce').fillna(0).astype(int)
    df['Attendance'] = pd.to_numeric(df['Attendance'], errors='coerce')

    # Pour les colonnes de conversion, on convertit en entier si possible, sinon on garde None
    for col in COLS_TO_CONVERT:
        if 'Score' in col:
            # Pour Score_Home et Score_Away, on souhaite que les valeurs invalides restent None
            df[col] = pd.to_numeric(df[col], errors='coerce').apply(lambda x: int(x) if pd.notnull(x) else None)
        else:
            # Pour 'Wk' et 'Attendance', on laisse le résultat numérique
            df[col] = pd.to_numeric(df[col], errors='coerce').apply(lambda x: int(x) if pd.notnull(x) else None)
        
    return df


def generate_csv_filename(url, df):
    """
    Génère un nom de fichier CSV basé sur l'URL et la saison extraite du DataFrame.
    """

    # Convertir la colonne 'Date' en datetime
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    if df['Date'].dropna().empty:
        raise ValueError("Aucune date valide trouvée dans le DataFrame.")
    
    # Extraire l'année de début et l'année de fin
    start_year = df['Date'].min().year
    end_year = df['Date'].max().year
    season = f"{start_year}-{end_year}"
    
    # Extraire le nom de la ligue en excluant certains mots
    def extract_league_name(url):
        last_part = url.split('/')[-1]
        elements = last_part.split('-')
        exclude = {"Scores", "and", "Fixtures"}
        league_parts = [el for el in elements if el not in exclude]
        return "-".join(league_parts)
    
    league_name = extract_league_name(url)
    
    return f"{league_name}-{season}.csv"


def save_to_csv(df, filename):
    """
    Saves the DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        filename (str): The name of the CSV file.
    """
    csv_path = CSV_DIR / filename
    df.to_csv(csv_path, index=False)

def process_fbref_data(url):
    """
    Processes FBref data from the given URL and saves it as a CSV.

    Args:
        url (str): The URL of the FBref page containing scores and fixtures.

    Returns:
        pd.DataFrame: The processed DataFrame.
    """
    # Fetch and clean data
    raw_data = fetch_table_from_url(url)
    cleaned_data = clean_and_transform_data(raw_data)
    
    # Generate CSV filename and save data
    csv_filename = generate_csv_filename(url, cleaned_data)
    save_to_csv(cleaned_data, csv_filename)
    
    return cleaned_data

# Usage
if __name__ == "__main__":
    url = "https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures"
    
    try:
        df = process_fbref_data(url)
        print("Data processed and saved successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")