from django.contrib import admin
from .models import Match, MatchDay, Team, League, Season

# Administration des matchs
@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("day","league","match_date","team_home","score_home","score_away","team_away","venue", "referee")
    list_filter = ("day__season", "league", "match_date")  # Filtrage par saison/ligue
    autocomplete_fields = ["team_home", "team_away"]  # Recherche rapide pour Team
    raw_id_fields = ["day"]  # Utile si beaucoup de journées
    search_fields = ("team_home__team_name", "team_away__team_name")
    
    fieldsets = (
        ("Infos générales", {
            "fields": ("match_date", "day", "league", "venue")
        }),
        ("Score", {
            "fields": (("team_home", "score_home"), ("team_away", "score_away")),
            "classes": ("collapse",)  # Peut être replié
        }),
    )
    
    list_select_related = (
        "day__season",  # Précharge season ET day en 1 requête
        "team_home",
        "team_away",
        "league"
    )
    
# Administration des MatchDay
@admin.register(MatchDay)
class MatchDayAdmin(admin.ModelAdmin):
    list_display = ("day_date","day_number","season")
    date_hierarchy = "day_date"  # Navigation temporelle


# Administration des Teams
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    search_fields = ["team_name", "short_name"]
    list_display = ["team_name", "short_name"]


# Administration des Leagues
@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    pass

# Administration des Seasons
@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ("season_name","start_date","end_date")