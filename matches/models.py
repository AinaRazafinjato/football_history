from django.db import models
from django.forms import ValidationError
from .constants import TEAM_MAPPING

class Season(models.Model):
    season_name = models.CharField(
        max_length=9,
        unique=True,
    )
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.season_name

class League(models.Model):
    league_name = models.CharField(
        max_length=100,
        unique=True
    )
    season = models.ForeignKey(
        Season, 
        on_delete=models.CASCADE,
        related_name="leagues", null=True, blank=True
    )

    def __str__(self):
        return self.league_name


class Team(models.Model):
    """
    Represents a team in the football history database.
    Attributes:
        team_name (str): The name of the team.
        short_name (str): The short name of the team (optional).
    Meta:
        ordering (list): The default ordering for Team objects.
    Methods:
        save(*args, **kwargs): Overrides the save method to calculate the short name if not defined.
        __str__(): Returns a string representation of the team.
    """
    team_name = models.CharField(max_length=150)
    short_name = models.CharField(max_length=10, null=True, blank=True)
    season = models.ForeignKey(
        Season, 
        on_delete=models.CASCADE,
        related_name="teams", null=True, blank=True
    )

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


class MatchDay(models.Model):
    day_number = models.IntegerField()
    day_date = models.DateField()
    season = models.ForeignKey(
        Season, 
        on_delete=models.CASCADE,
        related_name="match_days" 
    )
    
    class Meta:
        ordering = ["day_number"]

    def __str__(self):
        return f"Journée {self.day_number}"

class Match(models.Model):
    match_date = models.DateField()
    score_home = models.PositiveIntegerField(null=True, blank=True)
    score_away = models.PositiveIntegerField(null=True, blank=True)
    venue = models.CharField(max_length=100, null=True)
    referee = models.CharField(max_length=100, null=True)
    day = models.ForeignKey(MatchDay, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    team_home = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_matches")
    team_away = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_matches")
    season = models.ForeignKey(
        Season, 
        on_delete=models.CASCADE,
        related_name="matches", null=True, blank=True
    )
    
    def clean(self):
        if self.team_home == self.team_away:
            raise ValidationError("Une équipe ne peut pas jouer contre elle-même")
    
    class Meta:
        ordering = ["match_date", "day"]

    def __str__(self):
        return f"{self.match_date} - {self.team_home} vs {self.team_away}"