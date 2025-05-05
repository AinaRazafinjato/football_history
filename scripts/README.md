# 🏃 Runner de scripts - Football History

## 📝 Description
Le script `runner.py` est un orchestrateur qui permet d'exécuter facilement n'importe quel script Python dans le projet Football History sans avoir à naviguer manuellement vers le dossier du script ou à taper le chemin complet.

## ✨ Fonctionnalités
- 🔍 Découverte automatique de tous les scripts Python disponibles
- 📋 Liste complète des scripts disponibles
- ⚡ Exécution d'un script spécifique avec passage d'arguments

## 📚 Utilisation

### 🔍 Lister tous les scripts disponibles
Pour voir la liste de tous les scripts disponibles dans le projet :
```bash
python runner.py
```

### ▶️ Exécuter un script spécifique
Pour exécuter un script particulier avec des arguments :
```bash
python runner.py <script_id> [arguments]
```

**Exemple :**
```bash
python runner.py import_data/import_data --csv "Premier-League-2024-2025.csv"
```

## 📄 Scripts disponibles

### 📥 import_data/import_data
**Description:** Importe des données de matchs de football depuis des fichiers CSV vers la base de données Django.

**Fonctionnement:**
- Lit les données de matchs à partir d'un fichier CSV
- Extrait automatiquement le nom de la ligue et la saison
- Crée ou met à jour les équipes, la ligue, la saison et les journées de match
- Importe tous les matchs avec leurs informations détaillées (scores, lieu, arbitre, etc.)

**Options:**
- `--csv` : Nom du fichier CSV à importer (ex: "Premier-League-2024-2025.csv")

**Exemple:**
```bash
python runner.py import_data/import_data --csv "Premier-League-2024-2025.csv"
```

### 📤 export_data/export_data
**Description:** Exporte les données de matchs depuis le site FBref vers des fichiers CSV standardisés.

**Fonctionnement:**
- Récupère les données tabulaires depuis les pages FBref
- Nettoie et transforme les données (division des scores, conversion des types)
- Normalise les noms d'équipes selon les mappings définis dans constant.py
- Génère un nom de fichier basé sur la ligue et la saison
- Sauvegarde un fichier CSV prêt à être utilisé pour l'importation

**URL par défaut:** Premier League (https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures)

**Exemple:**
```bash
python runner.py export_data/export_data
```

### 🔤 export_data/constant
**Description:** Module contenant des constantes et des mappings pour standardiser les noms d'équipes.

**Exemple de mappings:**
- "Utd" → "United"
- "Nott'ham" → "Nottingham"
- "Wolves" → "Wolverhampton Wanderers"

**Utilisation:** Ce script est généralement importé par d'autres scripts et ne nécessite pas d'être exécuté directement.

### 🖼️ logo_scraper/logo_scraper
**Description:** Scrape et télécharge automatiquement les logos des équipes de football depuis SofaScore.

**Fonctionnement:**
- Utilise Playwright pour naviguer sur le site SofaScore
- Extrait les données du classement d'une ligue spécifique
- Télécharge les logos d'équipes, de pays et de ligues
- Standardise automatiquement les noms des équipes
- Enregistre les logos au format PNG dans le dossier media/logos

**URL par défaut:** Premier League (https://www.sofascore.com/tournament/football/england/premier-league/17)

**Exemple:**
```bash
python runner.py logo_scraper/logo_scraper
```

## 🔄 Flux de travail typique
1. **Récupérer les données de matchs depuis FBref:**
    ```bash
    python runner.py export_data/export_data
    ```

2. **Télécharger les logos des équipes:**
    ```bash
    python runner.py logo_scraper/logo_scraper
    ```

3. **Importer les données dans la base de données Django:**
    ```bash
    python runner.py import_data/import_data --csv "Premier-League-2024-2025.csv"
    ```

## 📁 Structure des répertoires
- `data/raw/csv/` : Stockage des fichiers CSV exportés et importés
- `static/logos/` : Stockage des logos téléchargés (équipes, ligues, pays)
- `logs/` : Stockage des fichiers journaux générés par les scripts

## ℹ️ Notes importantes
- Les scripts utilisent **Loguru** pour journaliser leurs opérations
- Les répertoires nécessaires sont créés automatiquement s'ils n'existent pas
- Les noms d'équipes sont standardisés selon les mappings définis
- Tous les scripts gèrent automatiquement les erreurs et produisent des messages détaillés
- Pour ajouter un nouveau script au système, il suffit de le placer dans un sous-répertoire approprié du dossier `scripts`. Il sera automatiquement détecté par le runner.