# REST API with Django (DRF) — Guide pratique (API seulement)

Objectif
- Exposer une API REST pour `Team` et `League` avec Django REST Framework (DRF). Ce guide documente aussi le comportement du sérializer pour retourner des URLs d'images valides (media/static).

Résumé des changements récents
- Les sérializers `LeagueSerializer` et `TeamSerializer` ont été créés et testés.
- Les sérializers renvoient maintenant `logo_url` absolues et robustes : ils cherchent d'abord le fichier dans `MEDIA_ROOT`, sinon ils tombent en back‑up sur la static files (`/static/...`).

Pourquoi c'est utile
- Certaines images sont stockées dans `media/` (upload via admin), d'autres sont présentes seulement dans `static/` (assets ajoutés manuellement). Le sérializer renverra une URL utilisable dans les deux cas.

---

Détails techniques (extrait utile)

- Le sérializer utilise une fonction utilitaire qui :
  - vérifie si `MEDIA_ROOT/<name>` existe -> retourne `MEDIA_URL + name`;
  - sinon tente `staticfiles_storage.url(name)` -> retourne `/static/...` si trouvé;
  - sinon utilise `static(name)` comme dernier recours.
- Les URLs retournées sont absolues via `request.build_absolute_uri()` quand le contexte `request` est disponible (DRF ViewSet le fournit automatiquement).

Exemple de réponse (Postman)

```
{
  "id": 1,
  "league_name": "Premier League",
  "logo_url": "http://127.0.0.1:8000/static/logos/leagues/Premier League.png",
  "country": "England"
}
```

Remarques pratiques
- Si votre image se trouve physiquement sous `static/logos/leagues/Premier League.png`, la réponse pointera vers `/static/logos/leagues/Premier League.png`.
- Si l'image est uploadée et se trouve dans `media/logos/leagues/...`, la réponse pointera vers `/media/logos/leagues/...`.
- Pour que l'URL soit accessible en dev, `MEDIA_URL`/`MEDIA_ROOT` sont configurés et `football_history/urls.py` expose bien `static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)`.

Tests rapides

```bash
# vérifier qu'une URL retournée renvoie 200 et type image
curl -I "http://127.0.0.1:8000/static/logos/leagues/Premier%20League.png"
# ou si media
curl -I "http://127.0.0.1:8000/media/logos/leagues/Premier%20League.png"
```

---

Si vous voulez que je :
- (A) renomme tous les champs pour retourner `logo` au lieu de `logo_url` (breaking change),
- (B) ajoute la vérification/normalisation automatique du champ `League.logo` (par ex. détecter et corriger les chemins manquants dans la base),
- (C) ajoute des exemples Postman et tests unitaires pour valider les URLs d'images,
indiquez la lettre correspondante.

---

**Outils Git (GitKraken wrapper)**

Vous pouvez utiliser les helpers exposés par l'environnement pour gérer l'état git depuis l'agent :

- **`mcp_gitkraken_git_status`** : lister le statut du dépôt (staged/unstaged), utile avant d'appliquer un changement de masse.
- **`mcp_gitkraken_git_worktree`** : gérer les worktrees (ex: créer un worktree pour une branche de migration). Exemple d'usage : créer une nouvelle branch/worktree pour appliquer des corrections sans toucher la branche principale.

Conseil rapide : exécutez `mcp_gitkraken_git_status` avant d'appliquer le script `normalize_logos --apply` et créez une branche dédiée (`normalize/logos-apply`) via `mcp_gitkraken_git_worktree` si vous voulez une révision isolée.

---

**API Reference — Leagues & Teams**

Base URL: `http://127.0.0.1:8000/api/`

1) List leagues
- Endpoint: `GET /api/leagues/`
- Query params: `?page=` (pagination), `?search=` (DRF SearchFilter if enabled)
- Response (200): paginated list of league objects.

Sample response (single item):

```json
{
  "id": 1,
  "league_name": "Premier League",
  "logo_url": "http://127.0.0.1:8000/static/logos/leagues/Premier League.png",
  "country": "England"
}
```

2) Retrieve league
- Endpoint: `GET /api/leagues/{id}/`
- Returns the league object (fields: `id`, `league_name`, `logo_url`, `country`).

3) List teams
- Endpoint: `GET /api/teams/`
- Query params: `?page=` (pagination), `?search=` (search on `team_name`), `?ordering=team_name`
- Each team contains nested `league` with `id` and `league_name`.

Sample team response (single item):

```json
{
  "id": 42,
  "team_name": "Arsenal",
  "short_name": "ARS",
  "logo_url": "http://127.0.0.1:8000/static/logos/teams/England/Premier League/Arsenal.png",
  "league": {
    "id": 1,
    "league_name": "Premier League",
    "logo_url": "http://127.0.0.1:8000/static/logos/leagues/Premier League.png",
    "country": "England"
  }
}
```

4) Retrieve team
- Endpoint: `GET /api/teams/{id}/`

Notes
- Pagination: DRF returns paginated results by default (`results` key). Use `?page=` to navigate.
- Absolute URLs: `logo_url` is absolute when `request` is present (browsable API / clients). If you see encoded spaces (`%20`) that's normal URL encoding — browsers handle it.
- If an image URL returns `/static/leagues/...` instead of `/static/logos/leagues/...`, exécutez la commande de normalisation `manage.py normalize_logos` en dry-run puis avec `--apply`.

---

Si vous voulez, j'ajoute une petite collection Postman (fichier JSON) et un script d'exemples `curl` pour valider ces endpoints automatiquement.
