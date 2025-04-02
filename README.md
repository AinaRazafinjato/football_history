### 🏆 **Football History - Extraction et Importation de Données**

Ce projet permet d'extraire des données de matchs depuis **FBref**, de les exporter en CSV, puis de les importer dans une base de données **SQLite** pour les exploiter dans une application Django.

---

## 🚀 Installation

1. **Cloner le projet**  
   ```bash
   git clone https://github.com/AinaRazafinjato/football_history.git
   cd football_history
   ``` 

2. **Créer et activer un environnement virtuel**  
   - Sur **Windows** :  
     ```bash
     python -m venv .env
     .env\Scripts\activate
     ```  
   - Sur **macOS/Linux** :  
     ```bash
     python3 -m venv .env
     source .env/bin/activate
     ```

3. **Installer les dépendances**  
   Assurez-vous d'avoir Python installé dans l'environnement virtuel, puis exécutez :  
   ```bash
   pip install -r requirements.txt
   ```

4. **Effectuer la migration vers la base de données SQLite**  
   Exécutez :  
   ```bash
   python manage.py migrate
   ```

---

## 📌 Gestion de Bootstrap

Ce projet utilise **Bootstrap** pour styliser l'interface de l'application. Pour que tous les développeurs aient accès aux mêmes styles et fonctionnalités, deux options s'offrent à vous :

### **1. Via CDN (recommandé)**

L'utilisation d'un CDN permet de charger Bootstrap directement depuis Internet. Ajoutez simplement les liens suivants dans la balise `<head>` de vos templates HTML :

```html
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" 
integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" 
integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>
```

> **Avantage :**  
> Vous n'avez pas besoin de gérer les fichiers localement, ce qui garantit que tout le monde utilise la même version de Bootstrap.

### **2. Fichiers locaux**

**Option 1 : Télécharger la version compilée (Compiled CSS and JS)**  
Rendez-vous sur la page officielle de téléchargement de Bootstrap :  
[Télécharger Bootstrap](https://getbootstrap.com/docs/5.3/getting-started/download/)  
Cliquez sur le bouton "Compiled CSS and JS" pour télécharger le fichier `dist`.

Décompressez l'archive et placez les dossiers **css** et **js** issus du dossier `dist` dans le répertoire `static/vendors/bootstrap/` de votre projet.

Dans vos templates HTML, modifiez les liens pour pointer vers ces fichiers :

```html
<link rel="stylesheet" href="{% static 'vendors/bootstrap/css/bootstrap.min.css' %}">
<script src="{% static 'vendors/bootstrap/js/bootstrap.bundle.min.js' %}"></script>
```

Assurez-vous que la configuration des fichiers statiques de Django est correctement effectuée.

---

## 📥 Exportation des Données

### 🔹 Étape 1 : Modifier l'URL de la ligue  
Si vous souhaitez exporter des données d'une autre ligue, procédez ainsi :  
1. Rendez-vous sur [FBref](https://fbref.com/en/)  
2. Allez dans l'onglet **"Scores & Fixtures"** de la ligue désirée  
3. Copiez l'URL de la page  
4. Ouvrez le fichier **`export_data.py`** et remplacez la valeur de la variable `url` par ce lien  

### 🔹 Étape 2 : Lancer l'exportation  
Exécutez le script :  
```bash
python export_data.py


Une fois terminé, un dossier **`csv/`** sera créé à la racine du projet. Le fichier exporté sera nommé selon le format suivant :  
```
<league><season>.csv
```
*Exemple :* `Premier-League-2023-2024.csv`

---

## 🗄 Importation des Données dans SQLite

1. Ouvrez le fichier **`import_data.py`**  
2. Modifiez la variable `csv_path` pour pointer vers le fichier CSV exporté, par exemple :  
   ```python
   csv_path = "csv/Premier-League-2023-2024.csv"
   ```
3. Exécutez le script d'importation :  
   ```bash
   python import_data.py
   ```
4. Les données seront importées dans la base **SQLite** du projet.

---

## 🚀 Lancement de l'Application

Une fois l'import des données terminé, démarrez le serveur Django pour visualiser l'application :  
```bash
python manage.py runserver
```
Ensuite, ouvrez votre navigateur et accédez à l'URL par défaut : [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## 📊 Visualisation des Données

Après l'importation, les données sont intégrées à l'application Django. Vous pouvez explorer l'interface web pour consulter et analyser ces données.

> **Note :**  
> Pour le moment, seule la **Premier League (Angleterre)** est prise en charge.

---

## 🔧 Améliorations Futures

- **Optimisation des modèles de données** pour une meilleure gestion des ajouts futurs  
- **Support d'autres ligues** sans modification manuelle du script  
- **Automatisation complète des processus d'export et d'import**

---

## 📩 Vos Retours

Si vous avez des suggestions ou des retours, notamment sur l'amélioration des modèles ou l'optimisation des processus, n'hésitez pas à m'en faire part !
