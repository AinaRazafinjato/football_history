from rest_framework import viewsets, filters
from .models import Team, League, Match
from .serializers import TeamSerializer, LeagueSerializer, MatchSerializer
import django_filters.rest_framework as df_filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

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
        return queryset.filter(Q(team_home__id=value) | Q(team_away__id=value))

class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Match.objects.select_related(
        'team_home', 'team_away', 'day__league_season__league', 'day__league_season__season'
    ).filter(score_home__isnull=False, score_away__isnull=False).all()
    serializer_class = MatchSerializer
    filterset_class = MatchFilter
    filter_backends = (df_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('team_home__team_name', 'team_away__team_name', 'day__league_season__league__league_name')
    ordering_fields = ('match_date', 'team_home__team_name')
    ordering = ('-match_date',)

    @action(detail=False, methods=['get'], url_path='total_goals')
    def total_goals(self, request):
        """
        Retourne JSON listant pour chaque équipe :
        - gp : matches joués
        - over_1_5 : matches où l'équipe a marqué > 1.5 buts
        - pct : pourcentage over_1_5 / gp * 100
        Filtrable via les mêmes query params que MatchViewSet (league, season, match_date_after/before, etc).
        """
        # apply DRF filters (filterset/search/ordering) first
        matches_qs = self.filter_queryset(self.get_queryset()).filter(
            score_home__isnull=False, score_away__isnull=False
        )

        teams = Team.objects.all().order_by('team_name')
        results = []

        for team in teams:
            gp_home = matches_qs.filter(team_home=team).count()
            gp_away = matches_qs.filter(team_away=team).count()
            gp = gp_home + gp_away

            over_home = matches_qs.filter(team_home=team, score_home__gt=1.5).count()
            over_away = matches_qs.filter(team_away=team, score_away__gt=1.5).count()
            over = over_home + over_away

            pct = round((over / gp) * 100, 2) if gp > 0 else 0.0

            results.append({
                'team_id': team.id,
                'team_name': team.team_name,
                'gp': gp,
                'over_1_5': over,
                'pct': pct,
            })

        return Response({'data': results})