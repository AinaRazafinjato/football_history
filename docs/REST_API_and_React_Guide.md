# REST API with Django (DRF) — Guide pratique (sans React)

Objectif
- Exposer une API REST pour `Team` et `League` avec Django REST Framework (DRF). Guide pas-à-pas pour appliquer les changements localement dans la codebase.

Prérequis
- Python 3.8+ et virtualenv (`.venv` activé)
- Projet Django présent (ce repo)

Sommaire rapide
1. Installer dépendances DRF (si manquant)
2. Configurer `settings.py` (STATIC/MEDIA/CORS/DRF)
3. Ajouter `matches/serializers.py`
4. Ajouter `matches/api_views.py` (ViewSets)
5. Enregistrer les routes via `DefaultRouter` (/api/)
6. Servir médias en dev et tester avec curl/Postman

---

Préparation — installer DRF (si nécessaire)
```bash
.venv\Scripts\Activate
pip install djangorestframework django-cors-headers
```

1) `settings.py` — vérifications et ajouts
 - Assurez-vous que `rest_framework` et `corsheaders` figurent dans `INSTALLED_APPS` (déjà présent dans ce projet).
 - Middleware: placez `corsheaders.middleware.CorsMiddleware` haut dans la liste (ou juste après `SecurityMiddleware`).
 - Ajoutez ces configurations utiles (extrait à insérer/valider) :

```py
# DRF
REST_FRAMEWORK = {
  'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
  'PAGE_SIZE': 20,
}

# CORS (dev) — autorise vos outils front (optionnel)
CORS_ALLOWED_ORIGINS = [
  'http://localhost:3000',
]

# Static & Media
STATIC_URL = '/static/'
STATICFILES_DIRS = [ os.path.join(BASE_DIR, 'static'), ]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

2) Créer `matches/serializers.py` (ajout)
 - Fichier à créer si absent; example minimal (mis à jour pour correspondre aux modèles actuels) :

```py
from rest_framework import serializers
from .models import Team, League

Ce fichier a été renommé et remplacé par `REST_API_DRF_Guide.md`.

Voir : [docs/REST_API_DRF_Guide.md](docs/REST_API_DRF_Guide.md)