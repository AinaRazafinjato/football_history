from django.db import models
from django.forms import ValidationError
from .constants import TEAM_MAPPING

class Season(models.Model):
    season_name = models.CharField(max_length=9, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    
    def __str__(self):
        return self.season_name
    
    class Meta:
        ordering = ['-start_date']  # Plus récent en premier

class League(models.Model):
    league_name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='logos/leagues/', null=True, blank=True)  # Nouveau champ
    country = models.CharField(max_length=100, null=True, blank=True)  # Nouveau champ
    
    def suggest_country(self):
        """Suggest a country based on league name"""
        league_country_mapping = {
            'Premier League': 'England',
            'La Liga': 'Spain',
            'Bundesliga': 'Germany',
            'Serie A': 'Italy',
            'Ligue 1': 'France',
            # Add more mappings as needed
        }
        
        for league_pattern, country in league_country_mapping.items():
            if league_pattern.lower() in self.league_name.lower():
                return country
        return None
    
    def save(self, *args, **kwargs):
        # Auto-fill country if it's not set and can be determined
        if not self.country:
            suggested_country = self.suggest_country()
            if suggested_country:
                self.country = suggested_country
        super().save(*args, **kwargs)
    
    
    def __str__(self):
        return self.league_name
    
    class Meta:
        ordering = ['country', 'league_name']

class LeagueSeason(models.Model):
    # Nouveau modèle pour lier les ligues et les saisons
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='seasons')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='leagues')
    
    class Meta:
        unique_together = ['league', 'season']
        
    def __str__(self):
        return f"{self.league} - {self.season}"

class Team(models.Model):
    team_name = models.CharField(max_length=150)
    short_name = models.CharField(max_length=10, null=True, blank=True)
    logo = models.ImageField(upload_to='logos/teams/', null=True, blank=True)  # Nouveau champ
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='teams', null=True, blank=True)  # Renamed from country for clarity
    
    class Meta:
        ordering = ["team_name"]

    def save(self, *args, **kwargs):
        if not self.short_name:
            found = False
            for short, full in TEAM_MAPPING.items():
                if self.team_name.strip().lower() == full.lower():
                    self.short_name = short
                    found = True
                    break
            if not found:
                self.short_name = self.team_name[:3].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.team_name

class TeamSeason(models.Model):
    # Nouveau modèle pour lier les équipes aux saisons/ligues
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='seasons')
    league_season = models.ForeignKey(LeagueSeason, on_delete=models.CASCADE, related_name='teams')
    
    class Meta:
        unique_together = ['team', 'league_season']
        
    def __str__(self):
        return f"{self.team} - {self.league_season}"

class MatchDay(models.Model):
    day_number = models.IntegerField()
    day_date = models.DateField()
    league_season = models.ForeignKey(LeagueSeason, on_delete=models.CASCADE, related_name="match_days", null=True, blank=True)
    
    class Meta:
        ordering = ["day_number"]
        unique_together = ['day_number', 'league_season']
    
    @property
    def season(self):
        return self.league_season.season
    
    def __str__(self):
        league_season_str = f" - {self.league_season}" if self.league_season else ""
        return f"Day {self.day_number}"
    
class Match(models.Model):
    match_date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    score_home = models.PositiveIntegerField(null=True, blank=True)
    score_away = models.PositiveIntegerField(null=True, blank=True)
    xG_home = models.FloatField(null=True, blank=True)
    xG_away = models.FloatField(null=True, blank=True)
    day = models.ForeignKey(MatchDay, on_delete=models.CASCADE, related_name='matches')
    team_home = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_matches")
    team_away = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_matches")
    
    def clean(self):
        if self.team_home == self.team_away:
            raise ValidationError("Une équipe ne peut pas jouer contre elle-même")
    
    class Meta:
        ordering = ["match_date", "day"]
        # Une équipe ne peut pas jouer deux fois le même jour
        unique_together = ['match_date', 'team_home', 'team_away']

    def __str__(self):
        score = ""
        if self.score_home is not None and self.score_away is not None:
            score = f" ({self.score_home}-{self.score_away})"
        return f"{self.match_date} - {self.team_home} vs {self.team_away}{score}"