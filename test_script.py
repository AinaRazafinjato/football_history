# Script python for testing

from matches.models import Match, MatchDay, League, Team

# Supprimer les matchs de la saison 2024-2025
Match.objects.filter(season__season_name="2024-2025").delete()
MatchDay.objects.filter(season__season_name="2024-2025").delete()
Team.objects.filter(season__season_name="2024-2025").delete()
League.objects.filter(season__season_name="2024-2025").delete()

print("Tous les matchs de la saison 2024-2025 ont été supprimés, mais la saison est conservée.")
