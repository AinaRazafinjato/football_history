from rest_framework import viewsets, filters
from .models import Team, League
from .serializers import TeamSerializer, LeagueSerializer

class TeamViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = Team.objects.select_related('league').all()
  serializer_class = TeamSerializer
  filter_backends = [filters.SearchFilter, filters.OrderingFilter]
  search_fields = ['team_name']
  ordering_fields = ['team_name']

class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = League.objects.all()
  serializer_class = LeagueSerializer