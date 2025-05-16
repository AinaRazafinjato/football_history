# 🏆 Football History - Extraction et Importation de Données

Ce projet permet d'extraire des données de matchs depuis **FBref**, de les exporter en CSV, puis de les importer dans une base de données **SQLite** pour les exploiter dans une application Django.

## 🚀 Installation

1. **Cloner le projet**  
   ```bash
   git clone https://github.com/AinaRazafinjato/football_history.git
   cd football_history
   ```

2. **Créer et activer un environnement virtuel**

   Sur Windows :
   ```bash
   python -m venv .env
   .env\Scripts\activate
   ```

   Sur macOS/Linux :
   ```bash
   python3 -m venv .env
   source .env/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Effectuer la migration vers la base de données SQLite**
   ```bash
   python manage.py migrate
   ```

## 🎮 Utilisation du Runner de Scripts

Pour faciliter l'exécution des différents scripts sans avoir à naviguer dans les dossiers ou à taper des chemins complets, le projet inclut un runner de scripts.

- **Lister tous les scripts disponibles**
  ```bash
  python scripts/runner.py
  ```

- **Exécuter un script spécifique**
  ```bash
  python scripts/runner.py <script_id> [arguments]
  ```

  Exemple :
  ```bash
  python scripts/runner.py import_data/import_data --csv "Premier-League-2024-2025.csv"
  ```

## 📄 Scripts disponibles

### 📥 import_data/import_data
Description : Importe des données de matchs depuis des fichiers CSV vers la base de données.

Options :
- `--csv` : Nom du fichier CSV à importer (ex: "Premier-League-2024-2025.csv")

### 📤 export_data/export_data
Description : Exporte les données de matchs depuis FBref vers des fichiers CSV.

Fonctionnement :
- Récupère les données depuis FBref
- Nettoie et normalise les noms d'équipes
- Enregistre un fichier CSV dans le dossier `csv`

### 🖼️ logo_scraper/logo_scraper
Description : Télécharge les logos des équipes de football depuis SofaScore.

Fonctionnement :
- Extrait les données du classement d'une ligue
- Télécharge les logos des équipes, pays et ligues
- Standardise les noms des fichiers
- Enregistre les logos au format PNG dans le dossier `media/logos/`

## 🔄 Flux de travail typique

```bash
# Étape 1 : Exporter les données (optionnel)
# Assurez-vous que le fichier CSV est présent dans le dossier `csv`
python scripts/runner.py export_data/export_data

# Étape 2 : Télécharger les logos (optionnel)
# Assurez-vous que les logos sont présents dans le dossier `static/logos/`
python scripts/runner.py logo_scraper/logo_scraper

# Étape 3 : Importer les données (obligatoire)
python scripts/runner.py import_data/import_data --csv "Premier-League-2024-2025.csv"
```

## 📌 Gestion de Bootstrap

Ce projet utilise Bootstrap pour styliser l'interface de l'application. Deux options s'offrent à vous :

### Fichiers locaux
- Télécharger la version compilée (Compiled CSS and JS) depuis la [page officielle de téléchargement de Bootstrap](https://getbootstrap.com/docs/5.0/getting-started/download/)
- Décompresser l'archive et placer les dossiers `css` et `js` dans le répertoire `bootstrap` de votre projet
- Dans vos templates HTML, modifier les liens :
  ```html
  <link rel="stylesheet" href="{% static 'vendors/bootstrap/css/bootstrap.min.css' %}">
  <script src="{% static 'vendors/bootstrap/js/bootstrap.bundle.min.js' %}"></script>
  ```

## 🚀 Lancement de l'Application

```bash
python manage.py runserver
```

## 📊 Visualisation des Données
Après l'importation, les données sont intégrées à l'application Django. Vous pouvez explorer l'interface web pour consulter et analyser ces données.

**Note :** Pour le moment, seule la Premier League (Angleterre) est prise en charge.

## 🔧 Améliorations Futures
- Optimisation des modèles de données pour une meilleure gestion des ajouts futurs
- Support d'autres ligues sans modification manuelle du script
- Automatisation complète des processus d'export et d'import

## 📁 Structure des répertoires principaux
- `csv` : Stockage des fichiers CSV exportés et importés
- `media/logos/` : Stockage des logos téléchargés (équipes, ligues, pays)
- `static` : Fichiers statiques pour l'application web
- `scripts` : Scripts utilitaires pour l'exportation et l'importation de données
- `matches` : Application Django pour la gestion des matchs
- `logs/` : Fichiers journaux générés par les scripts

## 📩 Vos Retours
Si vous avez des suggestions ou des retours, notamment sur l'amélioration des modèles ou l'optimisation des processus, n'hésitez pas à m'en faire part !
