from rest_framework import serializers
from django.conf import settings
from django.templatetags.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
import os

from .models import Team, League, MatchDay, Match


def _build_file_url(name, request=None):
    """Return absolute URL for a file name trying media then static.

    `name` is the stored file name (ImageField.name). The function checks
    MEDIA_ROOT for the file first and returns MEDIA_URL+name if present.
    Otherwise it falls back to the static files URL.
    """
    # try media
    media_path = os.path.join(settings.MEDIA_ROOT, name)
    if os.path.exists(media_path):
        url = settings.MEDIA_URL + name.replace(os.path.sep, '/')
    else:
        # try staticfiles (this will raise if not found, so wrap)
        try:
            url = staticfiles_storage.url(name)
        except Exception:
            # as a last resort, try building a static path under 'logos/'
            url = static(name)

    if request:
        return request.build_absolute_uri(url)
    return url


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
            'id',
            'match_date',
            'time',
            'team_home',
            'team_away',
            'score_home',
            'score_away',
            'xG_home',
            'xG_away',
            'day',
        ]