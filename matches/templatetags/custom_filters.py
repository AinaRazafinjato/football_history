from django import template
from .constants import TEAM_SHORTCUTS
from datetime import datetime, timedelta
from django.conf import settings
from django.templatetags.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
import os

register = template.Library()


@register.simple_tag(takes_context=True)
def logo_url(context, logo):
    """Return a URL for a logo that prefers MEDIA then static files.

    Usage in template:
      {% logo_url match.team_home.logo as home_logo %}
      <img src="{{ home_logo }}">
    """
    name = None
    if not logo:
        return ''
    # FieldFile or string
    name = getattr(logo, 'name', logo)
    if not name:
        return ''

    # prefer MEDIA if file exists there
    media_path = os.path.join(settings.MEDIA_ROOT, name)
    if os.path.exists(media_path):
        url = settings.MEDIA_URL + name.replace(os.path.sep, '/')
    else:
        try:
            url = staticfiles_storage.url(name)
        except Exception:
            url = static(name)

    request = context.get('request')
    if request:
        return request.build_absolute_uri(url)
    return url

@register.filter
def ajust_team_name(team):
    """Convertir les noms d'équipes longs en versions courtes."""
    # Convertir l'objet Team en string si nécessaire
    if not isinstance(team, str):
        team_name = str(team)  # Utilise la méthode __str__ de l'objet Team
    else:
        team_name = team
    
    # Vérifier si le nom est dans notre dictionnaire
    if team_name in TEAM_SHORTCUTS:
        return TEAM_SHORTCUTS[team_name]
    
    # Règle générale: si le nom est plus long que 12 caractères,prendre le premier mot (généralement le nom principal)
    if len(team_name) > 12:
        # Prendre le premier mot, sauf s'il s'agit de 'FC', 'AC', etc.
        words = team_name.split()
        if words and words[0] in ['FC', 'AC', 'AS', 'CD', 'SC', 'SS', 'RC']:
            return words[1] if len(words) > 1 else team_name
        return words[0] if words else team_name
    
    return team_name

@register.filter
def winner_class(team_type, match):
    """Retourne une classe CSS pour l'équipe gagnante"""
    if match.score_home is None or match.score_away is None:
        return ""
    
    if team_type == 'home':
        if match.score_home > match.score_away:
            return "fw-bold"
        elif match.score_home < match.score_away:
            return "text-muted"
    elif team_type == 'away':
        if match.score_away > match.score_home:
            return "fw-bold"
        elif match.score_away < match.score_home:
            return "text-muted"
        
    # Pour les matchs nuls, vous pourriez ajouter une classe spécifique
    if match.score_home == match.score_away:
        return "text-draw"
    
    return ""  # Match nul ou pas encore joué

@register.filter
def week_start(date_str):
    """Retourne le lundi de la semaine"""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    return (date_obj - timedelta(days=date_obj.weekday())).strftime('%Y-%m-%d')

@register.filter
def week_end(date_str):
    """Retourne le dimanche de la semaine"""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    return (date_obj - timedelta(days=date_obj.weekday()) + timedelta(days=6)).strftime('%Y-%m-%d')