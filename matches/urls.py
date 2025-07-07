from django.urls import path
from . import views

urlpatterns = [
    path('v1/', views.home_v1, name='home_v1'),
    path('v2/', views.home_v2, name='home_v2'),
    path('search/', views.search_matches, name='search_matches'),
    path('statistics/', views.statistics, name='statistics'),
    path('api/statistics/', views.statistics_api, name='statistics_api'),
]
