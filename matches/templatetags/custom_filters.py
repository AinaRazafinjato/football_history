from django import template
from .constants import TEAM_SHORTCUTS

register = template.Library()

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