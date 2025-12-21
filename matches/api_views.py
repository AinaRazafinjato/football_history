from rest_framework import viewsets, filters
from .models import Team, League, Match
from .serializers import TeamSerializer, LeagueSerializer, MatchSerializer
import django_filters.rest_framework as df_filters

class TeamViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = Team.objects.select_related('league').all()
  serializer_class = TeamSerializer
  filter_backends = [filters.SearchFilter, filters.OrderingFilter]
  search_fields = ['team_name']
  ordering_fields = ['team_name']

class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = League.objects.all()
  serializer_class = LeagueSerializer
  

class MatchFilter(df_filters.FilterSet):
    match_date_after = df_filters.DateFilter(field_name='match_date', lookup_expr='gte')
    match_date_before = df_filters.DateFilter(field_name='match_date', lookup_expr='lte')
    team = df_filters.NumberFilter(method='filter_by_team')  # id or use slug if you prefer
    league = df_filters.CharFilter(field_name='day__league_season__league__league_name', lookup_expr='iexact')
    season = df_filters.CharFilter(field_name='day__league_season__season__season_name', lookup_expr='iexact')

    class Meta:
        model = Match
        fields = ['match_date_after', 'match_date_before', 'team', 'league', 'season']

    def filter_by_team(self, queryset, name, value):
        return queryset.filter(models.Q(team_home__id=value) | models.Q(team_away__id=value))

class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Match.objects.select_related(
        'team_home', 'team_away', 'day__league_season__league', 'day__league_season__season'
    ).all()
    serializer_class = MatchSerializer
    filterset_class = MatchFilter
    search_fields = ['team_home__team_name', 'team_away__team_name', 'day__league_season__league__league_name']
    ordering_fields = ['match_date', 'team_home__team_name']
    ordering = ['-match_date']