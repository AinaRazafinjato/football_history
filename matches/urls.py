from rest_framework.routers import DefaultRouter
from django.urls import include
from django.urls import path
from . import views
from .api_views import TeamViewSet, LeagueViewSet, MatchViewSet

router = DefaultRouter()
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'leagues', LeagueViewSet, basename='league')
router.register(r'matches', MatchViewSet, basename='match')

urlpatterns = [
    path('v1/', views.home_v1, name='home_v1'),
    path('v2/', views.home_v2, name='home_v2'),
    path('search/', views.search_matches, name='search_matches'),
    path('statistics/', views.statistics, name='statistics'),
    path('api/statistics/', views.statistics_api, name='statistics_api'),
    path('api/', include(router.urls)),
]