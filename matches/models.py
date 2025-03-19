from django.db import models
from django.forms import ValidationError

class Season(models.Model):
    season_name = models.CharField(
        max_length=9,
        unique=True
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

    def __str__(self):
        return self.league_name

class Team(models.Model):
    team_name = models.CharField(max_length=150)

    class Meta:
        ordering = ["team_name"]
    
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
    venue = models.CharField(max_length=100)
    day = models.ForeignKey(MatchDay, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    team_home = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_matches")
    team_away = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_matches")
    
    def clean(self):
        if self.team_home == self.team_away:
            raise ValidationError("Une équipe ne peut pas jouer contre elle-même")
    
    class Meta:
        ordering = ["day", "match_date"]

    def __str__(self):
        return f"{self.match_date} - {self.team_home} vs {self.team_away}"