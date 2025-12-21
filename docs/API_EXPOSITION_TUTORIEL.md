# Tutoriel : Exposer une API REST (Django REST Framework)

Ce tutoriel étape‑par‑étape en français est conçu pour vous rendre autonome dans l'exposition d'API pour vos modèles Django (teams, leagues, matches, etc.). Il présente les bonnes pratiques, exemples exacts de code et commandes à exécuter. Niveau : débutant → intermédiaire.

**Plan**
- Pré-requis
- Installation et configuration
- Créer des Serializers
- Créer des ViewSets et filtres
- Enregistrer les routes (router)
- Gérer les images / logos (MEDIA vs STATIC)
- Pagination, recherche et tri
- Tests et vérification
- Bonnes pratiques & pièges courants

---

**Pré-requis**
- Python + virtualenv
- Projet Django fonctionnel (ici base: `manage.py` à la racine)
- Django REST Framework installé (voir plus bas)

1) Activer l'environnement virtuel (Windows PowerShell)

```powershell
.venv\\Scripts\\Activate
```

2) Installer dépendances utiles

```powershell
pip install djangorestframework django-filter
```

---

**1. Configuration minimale**

Dans `settings.py` :

- Ajouter aux `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'django_filters',
]
```

- Configurer `REST_FRAMEWORK` avec filtres par défaut et pagination :

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}
```

- Assurez-vous d'avoir `STATIC_URL`, `STATICFILES_DIRS`, `MEDIA_URL`, `MEDIA_ROOT` bien définis (développement). Ex :

```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

**2. Serializers (exemples)**

- Objectif : transformer vos modèles en JSON. Favorisez des champs explicites et évitez d'exposer tout `Model._meta`.

Exemples (fichiers: `matches/serializers.py`)

```python
from rest_framework import serializers
from .models import Team, League, Match, MatchDay

class LeagueSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = League
        fields = ('id', 'league_name', 'logo_url', 'country')

    def get_logo_url(self, obj):
        request = self.context.get('request')
        if not obj.logo:
            return None
        return _build_file_url(obj.logo.name, request=request)


class TeamSerializer(serializers.ModelSerializer):
    league = LeagueSerializer(read_only=True)
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ('id', 'team_name', 'short_name', 'logo_url', 'league')

    def get_logo_url(self, obj):
        request = self.context.get('request')
        if not obj.logo:
            return None
        return _build_file_url(obj.logo.name, request=request)
```

- `MatchSerializer` (imbriqué avec `TeamSerializer`) :

```python
class MatchDaySerializer(serializers.ModelSerializer):
    season = serializers.SerializerMethodField()
    league = serializers.SerializerMethodField()

    class Meta:
        model = MatchDay
        fields = ['day_number', 'day_date', 'season', 'league']

    def get_season(self, obj):
        return obj.season.season_name if obj.season else None

    def get_league(self, obj):
        return obj.league_season.league.league_name if obj.league_season and obj.league_season.league else None


class MatchSerializer(serializers.ModelSerializer):
    team_home = TeamSerializer(read_only=True)
    team_away = TeamSerializer(read_only=True)
    day = MatchDaySerializer(read_only=True)

    class Meta:
        model = Match
        fields = [
            'id', 'match_date', 'time', 'team_home', 'team_away',
            'score_home', 'score_away', 'xG_home', 'xG_away', 'day'
        ]
```

- Note : la fonction `_build_file_url(name, request)` est une utilité (déjà présente dans votre projet) qui retourne d'abord `MEDIA_URL` si le fichier existe physiquement, sinon tombe en fallback vers `staticfiles_storage.url` ou `static()` pour garantir une URL accessible.

---

**3. ViewSets & filtres**

- Utilisez `ReadOnlyModelViewSet` si l'API est publique en lecture seule.
- Optimisez les requêtes avec `select_related` / `prefetch_related`.
- Ajoutez un `FilterSet` pour filtres complexes (dates, équipe, ligue).

Exemple (fichier `matches/api_views.py`)

```python
from rest_framework import viewsets
from django_filters import rest_framework as df_filters
from rest_framework import filters
from .models import Match
from .serializers import MatchSerializer
from django.db import models

class MatchFilter(df_filters.FilterSet):
    match_date_after = df_filters.DateFilter(field_name='match_date', lookup_expr='gte')
    match_date_before = df_filters.DateFilter(field_name='match_date', lookup_expr='lte')
    team = df_filters.NumberFilter(method='filter_by_team')
    league = df_filters.CharFilter(field_name='day__league_season__league__league_name', lookup_expr='iexact')
    season = df_filters.CharFilter(field_name='day__league_season__season__season_name', lookup_expr='iexact')

    class Meta:
        model = Match
        fields = ['match_date_after', 'match_date_before', 'team', 'league', 'season']

    def filter_by_team(self, queryset, name, value):
        return queryset.filter(models.Q(team_home__id=value) | models.Q(team_away__id=value))


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Match.objects.select_related(
        'team_home', 'team_away', 'day__league_season__league', 'day__league_season__season'
    ).all()
    serializer_class = MatchSerializer
    filterset_class = MatchFilter
    search_fields = ['team_home__team_name', 'team_away__team_name', 'day__league_season__league__league_name']
    ordering_fields = ['match_date', 'team_home__team_name']
    ordering = ['-match_date']
```

---

**4. Router / URLs**

Dans `matches/urls.py` ou `football_history/urls.py` :

```python
from rest_framework.routers import DefaultRouter
from .api_views import TeamViewSet, LeagueViewSet, MatchViewSet

router = DefaultRouter()
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'leagues', LeagueViewSet, basename='league')
router.register(r'matches', MatchViewSet, basename='match')

urlpatterns = [
    path('api/', include(router.urls)),
]
```

---

**5. Gérer les images / logos (MEDIA vs STATIC)**

- Problème fréquent : vos images sont dans `static/` mais `ImageField` stocke `logo.name` comme si c'était en `media/` (ex: `/media/logos/..`), provoquant 404.

Solutions pratiques :
- Normaliser les noms de fichiers en base (`logo.name = 'logos/teams/...'`) et stocker les fichiers dans `static/logos/...` ou `media/logos/...` (choisissez une stratégie et tenez‑y‑vous).
- Utiliser un helper `_build_file_url(name, request)` :
  - cherche dans `MEDIA_ROOT` et retourne `MEDIA_URL + name` si le fichier existe
  - sinon, utilise `staticfiles_storage.url(name)` ou `static(name)`
  - ajoute `request.build_absolute_uri()` si `request` présent

Exemple d'utilisation dans Serializer :

```python
def get_logo_url(self, obj):
    request = self.context.get('request')
    if not obj.logo:
        return None
    return _build_file_url(obj.logo.name, request=request)
```

- Dans les templates, préférez un tag utilitaire (`{% logo_url obj.logo as url %}`) pour afficher l'URL, comme on l'a ajouté au projet.

---

**6. Pagination, recherche et tri**

- Pagination : page number par défaut (déjà config dans `REST_FRAMEWORK`).
- Recherche : `SearchFilter` permet `?search=Arsenal` sur `search_fields` définis.
- Tri : `OrderingFilter` permet `?ordering=match_date` ou `?ordering=-match_date`.

---

**7. Tests et vérification**

- Démarrer le serveur de dev :

```powershell
.venv\\Scripts\\python.exe manage.py runserver
```

- Exemples `curl` :

```bash
curl "http://127.0.0.1:8000/api/matches/?team=3&match_date_after=2024-08-01"
curl "http://127.0.0.1:8000/api/teams/" | jq .
```

- Vérifier le champ `logo_url` dans la réponse JSON — il doit pointer vers `/media/...` ou `/static/...` accessible.

- Créer tests simples (fichier `matches/tests_api.py`) :
  - Test serializer: serialize une instance et assert `logo_url` non vide
  - Test viewset: client API `self.client.get(reverse('match-list'))` et assert 200

---

**8. Bonnes pratiques & conseils (débutant)**

- Exposure minimal : ne renvoyez que les champs nécessaires.
- Préférez `ReadOnlyModelViewSet` pour APIs publiques en lecture seule.
- Optimisez les requêtes : `select_related` pour FK uniques, `prefetch_related` pour M2M/collections.
- Filtrage au niveau DB (django-filter) plutôt que filtrage en Python.
- Pour gros volumes, implémentez pagination et limite de page raisonnable (20–50).
- Sécurisez vos endpoints : ajoutez des permissions pour les endpoints non publics.
- Logs et debugging : activez `DEBUG` et utilisez `./manage.py runserver` pour voir les 404/erreurs de fichiers statiques.
- Tests : écrivez au moins un test unitaire par serializer et par viewset.
- Documentation : installez `drf-spectacular` ou `drf-yasg` pour générer la doc OpenAPI/Swagger.

---

**9. Pièges courants & solutions rapides**

- 404 sur `/media/...` alors que fichier est dans `static/` : normaliser les chemins ou utiliser `_build_file_url` et `normalize_logos` (outil présent dans votre repo).
- `SerializerMethodField` n'a pas accès à `request` → vérifier `context={'request': request}`: DRF fournit automatiquement `request` quand vous utilisez ViewSets + DefaultRouter.
- Utiliser `team.logo.url` en template sans garantie d'existence → `if team.logo` ou utilitaire `logo_url`.

---

**10. Checklist rapide avant de publier**
- [ ] Routes API enregistrées dans le router
- [ ] Serializers testés pour les champs sensibles
- [ ] ViewSets optimisés (`select_related` / `prefetch_related`)
- [ ] Filtres `django-filter` ajoutés si besoin
- [ ] Pagination et limites raisonnables
- [ ] Logos/images accessibles (tester `logo_url`)
- [ ] Tests unitaires pour serializers & viewsets
- [ ] Documentation OpenAPI (optionnel mais recommandé)

---

Si vous voulez, j'applique automatiquement les fichiers d'exemple (`MatchSerializer`, `MatchViewSet`, `matches/urls.py`) dans votre repo et j'ajoute un petit test unitaire. Souhaitez‑vous que j'ajoute ces fichiers maintenant ?
