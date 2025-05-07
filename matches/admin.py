from django.contrib import admin
from .models import Match, MatchDay, Team, League, Season, LeagueSeason, TeamSeason
from django import forms
from django.forms.widgets import TimeInput
from django.utils.safestring import mark_safe

# Créer un widget personnalisé pour l'heure en format 24h
class Time24HourWidget(TimeInput):
    input_type = 'time'
    format = '%H:%M'

# Formulaire personnalisé pour les matches
class MatchAdminForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = '__all__'
        widgets = {
            'time': Time24HourWidget(),
        }

# Administration des matchs
@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    form = MatchAdminForm  # Utiliser le formulaire personnalisé
    list_display = ("day", "match_date", "format_time", "team_home", "score_home", "score_away", "team_away", "get_league")
    list_filter = ("day__league_season__season", "team_home__league", "match_date")
    autocomplete_fields = ["team_home", "team_away"]
    raw_id_fields = ["day"]
    search_fields = ("team_home__team_name", "team_away__team_name")
    
    def get_league(self, obj):
        return obj.day.league_season.league
    get_league.short_description = "League"
    get_league.admin_order_field = "day__league_season__league"
    
    # Méthode pour formater l'heure en format 24h dans la liste
    def format_time(self, obj):
        if obj.time:
            return obj.time.strftime('%H:%M')
        return None
    format_time.short_description = "Time"
    format_time.admin_order_field = "time"
    
    fieldsets = (
        ("Infos générales", {
            "fields": ("match_date", "time", "day")
        }),
        ("Score", {
            "fields": (("team_home", "score_home"), ("team_away", "score_away")),
            "classes": ("collapse",)
        }),
        ("Statistiques", {
            "fields": ("xG_home", "xG_away"),
            "classes": ("collapse",)
        }),
    )
    
    list_select_related = (
        "day__league_season__season",
        "day__league_season__league",
        "team_home",
        "team_away",
    )
    
# Administration des MatchDay
@admin.register(MatchDay)
class MatchDayAdmin(admin.ModelAdmin):
    list_display = ("day_date", "day_number", "get_season", "get_league")
    list_filter = ("league_season__league", "league_season__season")
    date_hierarchy = "day_date"
    
    def get_season(self, obj):
        return obj.league_season.season
    get_season.short_description = "Season"
    get_season.admin_order_field = "league_season__season"
    
    def get_league(self, obj):
        return obj.league_season.league
    get_league.short_description = "League"
    get_league.admin_order_field = "league_season__league"

# Administration des Teams
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ["team_logo", "team_name", "short_name", "league"]
    list_filter = ["league"]
    search_fields = ["team_name", "short_name"]
    
    def team_logo(self, obj):
        if obj.logo:
            return mark_safe(f'<img src="/static/logos/{obj.logo}" width="30" height="30" />')
        return "-"
    team_logo.short_description = "Logo"

# Administration des TeamSeason
@admin.register(TeamSeason)
class TeamSeasonAdmin(admin.ModelAdmin):
    list_display = ["team", "get_league", "get_season"]
    list_filter = ["league_season__league", "league_season__season", "team"]
    
    def get_season(self, obj):
        return obj.league_season.season
    get_season.short_description = "Season"
    
    def get_league(self, obj):
        return obj.league_season.league
    get_league.short_description = "League"

# Administration des Leagues
@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ["league_logo", "league_name", "country"]
    list_filter = ["country"]
    search_fields = ["league_name", "country"]
    
    def league_logo(self, obj):
        if obj.logo:
            return mark_safe(f'<img src="/static/logos/{obj.logo}" width="30" height="30" />')
        return "-"
    league_logo.short_description = "Logo"

# Administration des LeagueSeason
@admin.register(LeagueSeason)
class LeagueSeasonAdmin(admin.ModelAdmin):
    list_display = ["league", "season"]
    list_filter = ["league", "season"]

# Administration des Seasons
@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ("season_name", "start_date", "end_date")
    search_fields = ["season_name"]